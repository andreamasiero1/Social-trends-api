# VARIABILI D'AMBIENTE DA CONFIGURARE SU RENDER

# Copia queste variabili nel pannello Environment del Web Service

# URL del database PostgreSQL (dal tuo database Render)

DATABASE_URL=postgresql://social_trends_user:hM5MIzSqMlbCZrb8412qekjnnqmEVlnw@dpg-d3bs0qj7mgec73a02d20-a.frankfurt-postgres.render.com:5432/social_trends_vmp7?sslmode=require

# URL base per i link di verifica (IMPORTANTE: cambia da localhost a render)

BASE_URL=https://social-trends-api.onrender.com

# Modalità test (metti false per produzione)

ACCEPT_TEST_KEYS=false

# Chiave segreta (genera una nuova per produzione)

SECRET_KEY=your-super-secret-production-key-here-change-this

# Email Configuration (opzionale - configurare solo se vuoi invio email automatico)

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=tua-email@gmail.com
SMTP_PASSWORD=tua-app-password-gmail
SMTP_FROM_EMAIL=tua-email@gmail.com

# Porta (Render la gestisce automaticamente, ma puoi specificarla)

PORT=10000
