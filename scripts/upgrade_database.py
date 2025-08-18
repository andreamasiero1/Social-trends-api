#!/usr/bin/env python3
"""
Script per aggiornare il database con il nuovo sistema utenti migliorato.
Esegui questo script per applicare tutti gli aggiornamenti necessari.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()

async def upgrade_database():
    """Applica tutti gli aggiornamenti al database."""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL non configurato")
        return False
    
    # Converti per asyncpg se necessario
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        print("🔄 Connessione al database...")
        conn = await asyncpg.connect(database_url)
        
        print("📊 Controllo stato attuale del database...")
        
        # Controlla se esiste già la tabella users
        users_table_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
        )
        
        if not users_table_exists:
            print("🆕 Creazione tabella users...")
            await conn.execute("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
                    email_verification_token TEXT,
                    registration_source TEXT NOT NULL DEFAULT 'direct',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)
            
            await conn.execute("""
                CREATE INDEX idx_users_email ON users (email);
                CREATE INDEX idx_users_verification_token ON users (email_verification_token);
            """)
            print("✅ Tabella users creata")
        else:
            print("✅ Tabella users già esistente")
        
        # Controlla e aggiorna tabella api_keys
        columns = await conn.fetch("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'api_keys'
        """)
        
        existing_columns = [row['column_name'] for row in columns]
        
        if 'user_id' not in existing_columns:
            print("🔄 Aggiornamento tabella api_keys...")
            await conn.execute("""
                ALTER TABLE api_keys 
                ADD COLUMN user_id INTEGER REFERENCES users(id),
                ADD COLUMN source TEXT NOT NULL DEFAULT 'direct',
                ADD COLUMN rapidapi_user_id TEXT;
            """)
            
            await conn.execute("""
                CREATE INDEX idx_api_keys_user_id ON api_keys (user_id);
                CREATE INDEX idx_api_keys_rapidapi_user_id ON api_keys (rapidapi_user_id);
            """)
            print("✅ Tabella api_keys aggiornata")
        else:
            print("✅ Tabella api_keys già aggiornata")
        
        # Crea tabella email_verifications
        verification_table_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'email_verifications')"
        )
        
        if not verification_table_exists:
            print("📧 Creazione tabella email_verifications...")
            await conn.execute("""
                CREATE TABLE email_verifications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    token TEXT NOT NULL UNIQUE,
                    expires_at TIMESTAMPTZ NOT NULL,
                    verified_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)
            print("✅ Tabella email_verifications creata")
        else:
            print("✅ Tabella email_verifications già esistente")
        
        # Crea o aggiorna la funzione generate_api_key_v2
        print("🔧 Aggiornamento funzioni del database...")
        await conn.execute("""
            CREATE OR REPLACE FUNCTION generate_api_key_v2(
                p_email TEXT, 
                p_tier TEXT DEFAULT 'free',
                p_source TEXT DEFAULT 'direct',
                p_rapidapi_user_id TEXT DEFAULT NULL
            )
            RETURNS JSON AS $$
            DECLARE
                v_user_id INTEGER;
                v_key TEXT;
                v_limit INTEGER;
                v_requires_verification BOOLEAN := FALSE;
            BEGIN
                -- Determina il limite in base al tier
                CASE p_tier
                    WHEN 'free' THEN v_limit := 1000;
                    WHEN 'developer' THEN v_limit := 10000;
                    WHEN 'business' THEN v_limit := 50000;
                    WHEN 'enterprise' THEN v_limit := 200000;
                    ELSE v_limit := 1000;
                END CASE;
                
                -- Se è da RapidAPI, non serve verifica email
                IF p_source = 'rapidapi' THEN
                    v_requires_verification := FALSE;
                ELSE
                    v_requires_verification := TRUE;
                END IF;
                
                -- Controlla se l'utente esiste già
                SELECT id INTO v_user_id FROM users WHERE email = p_email;
                
                IF v_user_id IS NULL THEN
                    -- Crea nuovo utente
                    INSERT INTO users (email, is_email_verified, registration_source)
                    VALUES (p_email, NOT v_requires_verification, p_source)
                    RETURNING id INTO v_user_id;
                END IF;
                
                -- Genera chiave API
                v_key := CASE 
                    WHEN p_source = 'rapidapi' THEN 'rapid_' || encode(gen_random_bytes(16), 'hex')
                    ELSE 'api_' || encode(gen_random_bytes(16), 'hex')
                END;
                
                -- Inserisci API key
                INSERT INTO api_keys (key, user_id, tier, monthly_limit, source, rapidapi_user_id)
                VALUES (v_key, v_user_id, p_tier, v_limit, p_source, p_rapidapi_user_id);
                
                -- Ritorna risultato
                RETURN json_build_object(
                    'api_key', v_key,
                    'user_id', v_user_id,
                    'requires_email_verification', v_requires_verification,
                    'tier', p_tier,
                    'monthly_limit', v_limit
                );
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("✅ Funzioni del database aggiornate")
        
        # Migra API keys esistenti
        print("🔄 Migrazione API keys esistenti...")
        existing_keys = await conn.fetch("SELECT * FROM api_keys WHERE user_id IS NULL")
        
        migrated = 0
        for key_record in existing_keys:
            if key_record['user_email']:
                # Crea o trova l'utente
                user_id = await conn.fetchval("""
                    INSERT INTO users (email, is_email_verified, registration_source)
                    VALUES ($1, TRUE, 'legacy')
                    ON CONFLICT (email) DO UPDATE SET updated_at = NOW()
                    RETURNING id
                """, key_record['user_email'])
                
                if not user_id:
                    user_id = await conn.fetchval(
                        "SELECT id FROM users WHERE email = $1", 
                        key_record['user_email']
                    )
                
                # Aggiorna la chiave API
                await conn.execute("""
                    UPDATE api_keys 
                    SET user_id = $1, source = 'legacy'
                    WHERE id = $2
                """, user_id, key_record['id'])
                
                migrated += 1
        
        print(f"✅ {migrated} API keys migrate al nuovo sistema")
        
        # Inserisci chiavi di test aggiornate
        print("🧪 Aggiornamento chiavi di test...")
        test_user_id = await conn.fetchval("""
            INSERT INTO users (email, is_email_verified, registration_source)
            VALUES ('test@social-trends-api.com', TRUE, 'test')
            ON CONFLICT (email) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """)
        
        await conn.execute("""
            INSERT INTO api_keys (key, user_id, tier, monthly_limit, source) VALUES
            ('test_free_key_123', $1, 'free', 1000, 'test'),
            ('test_premium_key_456', $1, 'developer', 10000, 'test'),
            ('test_enterprise_key_789', $1, 'business', 50000, 'test')
            ON CONFLICT (key) DO NOTHING
        """, test_user_id)
        
        await conn.close()
        
        print("\n🎉 AGGIORNAMENTO COMPLETATO CON SUCCESSO!")
        print("\n📋 Nuove funzionalità disponibili:")
        print("   • Registrazione utenti con verifica email")
        print("   • Integrazione completa con RapidAPI")
        print("   • Sistema di tracciamento utenti migliorato")
        print("   • Endpoint per gestione account")
        print("\n🚀 Fai il deploy per attivare le nuove funzionalità!")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante l'aggiornamento: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(upgrade_database())
    exit(0 if success else 1)
