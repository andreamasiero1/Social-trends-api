-- Schema aggiornato per sistema utenti migliorato
-- Esegui questo script per aggiornare il database esistente

-- Tabella per gestire gli utenti
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    email_verification_token TEXT,
    registration_source TEXT NOT NULL DEFAULT 'direct', -- 'direct' o 'rapidapi'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Aggiorna tabella api_keys per collegarla agli utenti
ALTER TABLE api_keys 
ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id),
ADD COLUMN IF NOT EXISTS source TEXT NOT NULL DEFAULT 'direct', -- 'direct' o 'rapidapi'
ADD COLUMN IF NOT EXISTS rapidapi_user_id TEXT; -- ID utente di RapidAPI

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_verification_token ON users (email_verification_token);
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys (user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_rapidapi_user_id ON api_keys (rapidapi_user_id);

-- Tabella per tracciare le verifiche email
CREATE TABLE IF NOT EXISTS email_verifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Funzione aggiornata per generare API keys con supporto RapidAPI
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
    
    -- Ritorna risultato con info per verifica email se necessaria
    RETURN json_build_object(
        'api_key', v_key,
        'user_id', v_user_id,
        'requires_email_verification', v_requires_verification,
        'tier', p_tier,
        'monthly_limit', v_limit
    );
END;
$$ LANGUAGE plpgsql;

-- Migra le API keys esistenti al nuovo sistema
DO $$
DECLARE
    api_record RECORD;
    new_user_id INTEGER;
BEGIN
    FOR api_record IN SELECT * FROM api_keys WHERE user_id IS NULL LOOP
        -- Crea utente per ogni email esistente
        IF api_record.user_email IS NOT NULL THEN
            INSERT INTO users (email, is_email_verified, registration_source)
            VALUES (api_record.user_email, TRUE, 'legacy')
            ON CONFLICT (email) DO NOTHING
            RETURNING id INTO new_user_id;
            
            -- Se l'utente già esisteva, recupera l'ID
            IF new_user_id IS NULL THEN
                SELECT id INTO new_user_id FROM users WHERE email = api_record.user_email;
            END IF;
            
            -- Aggiorna la chiave API
            UPDATE api_keys 
            SET user_id = new_user_id, source = 'legacy'
            WHERE id = api_record.id;
        END IF;
    END LOOP;
END $$;

-- Test keys aggiornate per includere il nuovo sistema
INSERT INTO api_keys (key, user_id, tier, monthly_limit, source) VALUES
('test_free_key_123', 1, 'free', 1000, 'direct'),
('test_premium_key_456', 1, 'developer', 10000, 'direct'),
('test_enterprise_key_789', 1, 'business', 50000, 'direct')
ON CONFLICT (key) DO NOTHING;
