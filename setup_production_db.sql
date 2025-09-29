-- Script completo per setup database produzione Render
-- Esegui questo script nel database PostgreSQL di Render

-- 1. ESTENSIONI NECESSARIE
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2. TABELLE BASE (se non esistono già)

-- Tabella utenti
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    email_verification_token TEXT,
    registration_source TEXT NOT NULL DEFAULT 'direct', -- 'direct', 'rapidapi', 'instant'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabella API keys
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    user_email TEXT, -- campo legacy per compatibilità
    tier TEXT NOT NULL DEFAULT 'free',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    usage_count INTEGER NOT NULL DEFAULT 0,
    monthly_limit INTEGER NOT NULL DEFAULT 1000,
    source TEXT NOT NULL DEFAULT 'direct', -- 'direct', 'rapidapi', 'instant'
    rapidapi_user_id TEXT, -- ID utente di RapidAPI
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used TIMESTAMPTZ
);

-- Tabella utilizzo API
CREATE TABLE IF NOT EXISTS api_usage (
    id SERIAL PRIMARY KEY,
    api_key TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    response_time FLOAT,
    status_code INTEGER
);

-- Tabelle trends (per i dati dell'API)
CREATE TABLE IF NOT EXISTS trends (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    volume INTEGER NOT NULL,
    platform TEXT NOT NULL,
    country_code TEXT NOT NULL DEFAULT 'global',
    lang TEXT,
    metadata JSONB,
    time TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. INDICI PER PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys (key);
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys (user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_key_time ON api_usage (api_key, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trends_platform_time ON trends (platform, time DESC);

-- 4. FUNZIONE GENERATE_API_KEY_V2 (CRITICA PER L'API)
CREATE OR REPLACE FUNCTION generate_api_key_v2(
    p_email TEXT, 
    p_tier TEXT DEFAULT 'free',
    p_source TEXT DEFAULT 'instant',
    p_rapidapi_user_id TEXT DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
    v_user_id INTEGER;
    v_key TEXT;
    v_limit INTEGER;
BEGIN
    -- Determina il limite mensile basato sul tier
    CASE p_tier
        WHEN 'free' THEN v_limit := 1000;
        WHEN 'developer' THEN v_limit := 10000;
        WHEN 'business' THEN v_limit := 50000;
        WHEN 'enterprise' THEN v_limit := 200000;
        ELSE v_limit := 1000;
    END CASE;
    
    -- Controlla se l'utente esiste già
    SELECT id INTO v_user_id FROM users WHERE email = p_email;
    
    IF v_user_id IS NULL THEN
        -- Crea nuovo utente (sempre verificato per registrazione istantanea)
        INSERT INTO users (email, is_email_verified, registration_source)
        VALUES (p_email, TRUE, p_source)
        RETURNING id INTO v_user_id;
    ELSE
        -- Se l'utente esiste già, errore (email duplicata)
        RETURN json_build_object(
            'success', false,
            'error', 'email_already_exists',
            'message', 'Email già registrata'
        );
    END IF;
    
    -- Genera chiave API sicura
    v_key := CASE 
        WHEN p_source = 'rapidapi' THEN 'sk-rapid-' || encode(gen_random_bytes(20), 'hex')
        WHEN p_source = 'instant' THEN 'sk-proj-' || encode(gen_random_bytes(20), 'hex')  
        ELSE 'sk-api-' || encode(gen_random_bytes(20), 'hex')
    END;
    
    -- Inserisci API key nel database
    INSERT INTO api_keys (key, user_id, user_email, tier, monthly_limit, source, rapidapi_user_id, is_active)
    VALUES (v_key, v_user_id, p_email, p_tier, v_limit, p_source, p_rapidapi_user_id, TRUE);
    
    -- Ritorna risultato con successo
    RETURN json_build_object(
        'success', true,
        'api_key', v_key,
        'user_id', v_user_id,
        'tier', p_tier,
        'monthly_limit', v_limit,
        'source', p_source
    );
    
EXCEPTION WHEN OTHERS THEN
    -- Gestione errori
    RETURN json_build_object(
        'success', false,
        'error', 'database_error',
        'message', SQLERRM
    );
END;
$$ LANGUAGE plpgsql;

-- 5. FUNZIONE LEGACY PER COMPATIBILITÀ
CREATE OR REPLACE FUNCTION generate_api_key(p_email TEXT, p_tier TEXT DEFAULT 'free')
RETURNS TEXT AS $$
DECLARE
    v_result JSON;
    v_key TEXT;
BEGIN
    -- Usa la nuova funzione
    SELECT generate_api_key_v2(p_email, p_tier, 'legacy') INTO v_result;
    
    -- Estrai la chiave dal JSON
    SELECT v_result->>'api_key' INTO v_key;
    
    -- Se c'è un errore, solleva eccezione
    IF (v_result->>'success')::boolean = FALSE THEN
        RAISE EXCEPTION '%', v_result->>'message';
    END IF;
    
    RETURN v_key;
END;
$$ LANGUAGE plpgsql;

-- 6. DATI DI TEST (opzionale)
INSERT INTO users (email, is_email_verified, registration_source) VALUES
('demo@example.com', TRUE, 'demo'),
('test@example.com', TRUE, 'demo')
ON CONFLICT (email) DO NOTHING;

-- Inserisci API keys di test
INSERT INTO api_keys (key, user_email, tier, monthly_limit, source, is_active) VALUES
('sk-demo-test-key-for-docs', 'demo@example.com', 'free', 1000, 'demo', TRUE),
('sk-test-dev-key-12345', 'test@example.com', 'developer', 10000, 'demo', TRUE)
ON CONFLICT (key) DO NOTHING;

-- 7. ALCUNI TREND DI ESEMPIO
INSERT INTO trends (name, volume, platform, country_code, time) VALUES
('#AI', 2500000, 'tiktok', 'global', NOW() - INTERVAL '1 hour'),
('#ChatGPT', 1800000, 'tiktok', 'global', NOW() - INTERVAL '2 hours'),
('#Tech', 1200000, 'instagram', 'global', NOW() - INTERVAL '1 hour'),
('#Innovation', 950000, 'instagram', 'global', NOW() - INTERVAL '3 hours'),
('#Startup', 800000, 'tiktok', 'global', NOW() - INTERVAL '4 hours')
ON CONFLICT DO NOTHING;

-- Fine script
-- Se tutto è andato bene, il database è ora configurato per l'API Social Trends!