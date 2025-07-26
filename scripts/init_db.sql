-- Estensione TimescaleDB per serie temporali
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Tabella principale per i trend
CREATE TABLE trends (
    id SERIAL,
    name TEXT NOT NULL,
    volume INTEGER NOT NULL,
    platform TEXT NOT NULL,
    country_code TEXT NOT NULL DEFAULT 'global',
    lang TEXT,
    metadata JSONB,
    time TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Converti in ipertabella TimescaleDB
SELECT create_hypertable('trends', 'time');

-- Tabella per le menzioni di keyword
CREATE TABLE mentions (
    id SERIAL,
    keyword TEXT NOT NULL,
    volume INTEGER NOT NULL,
    platform TEXT NOT NULL,
    sentiment FLOAT DEFAULT 0.5,
    metadata JSONB,
    time TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

SELECT create_hypertable('mentions', 'time');

-- Tabella per relazioni tra hashtag
CREATE TABLE hashtag_relations (
    id SERIAL,
    main_hashtag TEXT NOT NULL,
    related_hashtag TEXT NOT NULL,
    platform TEXT NOT NULL,
    volume INTEGER NOT NULL DEFAULT 0,
    time TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

SELECT create_hypertable('hashtag_relations', 'time');

-- Tabella per gestire le API keys degli utenti
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    user_email TEXT,
    tier TEXT NOT NULL DEFAULT 'free',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    usage_count INTEGER NOT NULL DEFAULT 0,
    monthly_limit INTEGER NOT NULL DEFAULT 1000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used TIMESTAMPTZ
);

-- Tabella per tracciare l'utilizzo delle API
CREATE TABLE api_usage (
    id SERIAL PRIMARY KEY,
    api_key TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    response_time FLOAT,
    status_code INTEGER
);

-- Indici per migliorare le performance
CREATE INDEX idx_trends_name_time ON trends (name, time DESC);
CREATE INDEX idx_trends_platform_time ON trends (platform, time DESC);
CREATE INDEX idx_mentions_keyword_time ON mentions (keyword, time DESC);
CREATE INDEX idx_hashtag_main ON hashtag_relations (main_hashtag);
CREATE INDEX idx_api_keys_key ON api_keys (key);

-- Inserisci alcune API keys di sviluppo
INSERT INTO api_keys (key, user_email, tier, monthly_limit) VALUES
('demo-key-12345', 'demo@example.com', 'free', 1000),
('dev-key-67890', 'dev@example.com', 'developer', 10000),
('test-key-andrea', 'andrea@test.com', 'business', 50000);

-- Inserisci alcuni dati di esempio per test
INSERT INTO trends (name, volume, platform, time) VALUES
('#fyp', 1200000, 'tiktok', NOW() - INTERVAL '1 hour'),
('#viral', 950000, 'tiktok', NOW() - INTERVAL '2 hours'),
('#dance', 800000, 'tiktok', NOW() - INTERVAL '3 hours'),
('#instagood', 1100000, 'instagram', NOW() - INTERVAL '1 hour'),
('#photooftheday', 890000, 'instagram', NOW() - INTERVAL '2 hours'),
('#fashion', 750000, 'instagram', NOW() - INTERVAL '3 hours');

-- Inserisci alcuni hashtag correlati di esempio
INSERT INTO hashtag_relations (main_hashtag, related_hashtag, platform, volume) VALUES
('fyp', 'viral', 'tiktok', 500000),
('fyp', 'trending', 'tiktok', 400000),
('instagood', 'photooftheday', 'instagram', 600000),
('fashion', 'style', 'instagram', 450000);

-- Funzione per generare nuove API keys
CREATE OR REPLACE FUNCTION generate_api_key(p_email TEXT, p_tier TEXT DEFAULT 'free')
RETURNS TEXT AS $$
DECLARE
    v_key TEXT;
    v_limit INTEGER;
BEGIN
    -- Determina il limite in base al tier
    CASE p_tier
        WHEN 'free' THEN v_limit := 1000;
        WHEN 'developer' THEN v_limit := 10000;
        WHEN 'business' THEN v_limit := 50000;
        WHEN 'enterprise' THEN v_limit := 200000;
        ELSE v_limit := 1000;
    END CASE;
    
    -- Genera chiave random
    v_key := 'api-' || encode(gen_random_bytes(16), 'hex');
    
    -- Inserisci nel database
    INSERT INTO api_keys (key, user_email, tier, monthly_limit)
    VALUES (v_key, p_email, p_tier, v_limit);
    
    RETURN v_key;
END;
$$ LANGUAGE plpgsql;
