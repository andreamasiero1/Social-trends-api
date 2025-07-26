#!/usr/bin/env python3
"""
Script per testare la connessione al database PostgreSQL su Render
e inizializzare le tabelle necessarie
"""

import asyncio
import asyncpg

# ⚠️ SOSTITUISCI questo URL con quello che ottieni da Render
DATABASE_URL = "postgresql://social_trends_user:Mrc3NbHY6XsRUsFt6qaQOefnVcPGLPYE@dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com/social_trends"

async def test_and_setup():
    """Testa la connessione e inizializza il database"""
    
    if DATABASE_URL == "INSERISCI_QUI_IL_TUO_DATABASE_URL_DA_RENDER":
        print("❌ Prima di eseguire questo script:")
        print("1. Sostituisci DATABASE_URL con l'Internal Database URL da Render")
        print("2. Verifica che entrambi i servizi siano 'Live' su Render")
        return
    
    try:
        print("🔗 Connessione al database Render...")
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Test connessione
        version = await conn.fetchval("SELECT version()")
        print(f"✅ Connessione riuscita!")
        print(f"📊 PostgreSQL version: {version[:50]}...")
        
        print("\n🛠️  Creazione tabelle...")
        
        # Crea tabella API keys
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                tier VARCHAR(50) NOT NULL DEFAULT 'free',
                requests_today INTEGER DEFAULT 0,
                requests_month INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            );
        """)
        print("✅ Tabella api_keys creata")
        
        # Aggiungi colonne mancanti se non esistono
        try:
            await conn.execute("ALTER TABLE api_keys ADD COLUMN IF NOT EXISTS usage_count INTEGER DEFAULT 0")
            await conn.execute("ALTER TABLE api_keys ADD COLUMN IF NOT EXISTS last_used TIMESTAMP")
            print("✅ Colonne aggiuntive aggiunte alla tabella api_keys")
        except Exception as e:
            print(f"⚠️  Errore aggiungendo colonne: {e}")
        
        # Crea tabella trends
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS trends (
                id SERIAL PRIMARY KEY,
                platform VARCHAR(50) NOT NULL,
                country VARCHAR(10),
                keyword VARCHAR(255),
                trend_data JSONB NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Tabella trends creata")
        
        # Crea tabella api_usage per il tracking delle richieste
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id SERIAL PRIMARY KEY,
                api_key VARCHAR(255) NOT NULL,
                endpoint VARCHAR(255) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address INET,
                user_agent TEXT
            );
        """)
        print("✅ Tabella api_usage creata")
        
        # Inserisci API keys di test
        test_keys = [
            ('test_free_key_123', 'test@example.com', 'free'),
            ('test_premium_key_456', 'premium@example.com', 'premium'),
            ('test_enterprise_key_789', 'enterprise@example.com', 'enterprise')
        ]
        
        for key, email, tier in test_keys:
            await conn.execute("""
                INSERT INTO api_keys (key, user_email, tier) 
                VALUES ($1, $2, $3) 
                ON CONFLICT (key) DO NOTHING
            """, key, email, tier)
        
        print("✅ API keys di test inserite")
        
        # Verifica setup
        count = await conn.fetchval("SELECT COUNT(*) FROM api_keys")
        print(f"📊 API keys totali: {count}")
        
        # Test query API keys
        keys = await conn.fetch("SELECT key, user_email, tier FROM api_keys LIMIT 3")
        print("\n🔑 API Keys disponibili:")
        for key in keys:
            print(f"  - {key['key']}: {key['user_email']} ({key['tier']})")
        
        await conn.close()
        print("\n🎉 Database inizializzato con successo!")
        print("\n📋 Prossimi passi:")
        print("1. Testa l'API su: https://your-app.onrender.com/docs")
        print("2. Usa una delle API keys sopra per testare gli endpoint")
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        print("\n🔍 Verifica che:")
        print("- Il DATABASE_URL sia corretto")
        print("- Il database sia 'Live' su Render")
        print("- Non ci siano errori di rete")

if __name__ == "__main__":
    asyncio.run(test_and_setup())
