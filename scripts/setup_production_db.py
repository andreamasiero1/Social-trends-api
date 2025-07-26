#!/usr/bin/env python3
"""
Script per inizializzare il database PostgreSQL in produzione
Esegui questo script dopo aver deployato su Render
"""

import asyncio
import asyncpg
import os
from datetime import datetime

# URL del database da Render (da settare come variabile d'ambiente)
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    # Fallback per costruire l'URL dalle singole variabili
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'social_trends_user')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_SERVER = os.getenv('POSTGRES_SERVER')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'social_trends')
    
    if all([POSTGRES_PASSWORD, POSTGRES_SERVER]):
        DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

async def setup_database():
    """Inizializza il database con le tabelle necessarie"""
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL non trovato nelle variabili d'ambiente")
        return
    
    try:
        print("🔗 Connessione al database...")
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Crea estensione TimescaleDB se disponibile
        try:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
            print("✅ Estensione TimescaleDB attivata")
        except Exception as e:
            print(f"⚠️  TimescaleDB non disponibile: {e}")
        
        # Crea tabella API keys
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                tier VARCHAR(50) NOT NULL DEFAULT 'free',
                requests_today INTEGER DEFAULT 0,
                requests_month INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            );
        """)
        print("✅ Tabella api_keys creata")
        
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
        
        # Crea hypertable per TimescaleDB se disponibile
        try:
            await conn.execute("SELECT create_hypertable('trends', 'timestamp', if_not_exists => TRUE);")
            print("✅ Hypertable TimescaleDB creata per trends")
        except Exception as e:
            print(f"⚠️  Hypertable non creata: {e}")
        
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
        print(f"📊 Numero API keys nel database: {count}")
        
        await conn.close()
        print("🎉 Database inizializzato con successo!")
        
    except Exception as e:
        print(f"❌ Errore durante l'inizializzazione: {e}")

if __name__ == "__main__":
    asyncio.run(setup_database())
