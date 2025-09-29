import os, sys
import psycopg2
import ssl
from datetime import datetime, timezone

# Usa variabile di ambiente DATABASE_URL se presente (accetta formato senza +asyncpg)
raw_url = os.getenv('DATABASE_URL')
if raw_url and '+asyncpg://' in raw_url:
    # converte in forma compatibile psycopg2
    raw_url = raw_url.replace('+asyncpg', '')
else:
    raw_url = raw_url or 'postgresql://social_trends_user:CHANGE_ME_PASSWORD@dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com:5432/social_trends?sslmode=require'

now_utc = datetime.now(timezone.utc).isoformat()
print(f"[INFO] {now_utc} Tentativo connessione psycopg2")
print(f"[INFO] URL (sanitizzato): {raw_url.split('@')[-1]}")

try:
    conn = psycopg2.connect(raw_url, connect_timeout=8)
    cur = conn.cursor()
    cur.execute('SELECT version();')
    v = cur.fetchone()[0]
    print('[SUCCESS] Connected. Version:', v)
    cur.close()
    conn.close()
except Exception as e:
    print('[ERROR] Exception type:', type(e).__name__)
    print('[ERROR] Message:', e)
    # Dump attributes utili
    for attr in ('pgcode','pgerror','diag'):
        if hasattr(e, attr) and getattr(e, attr):
            print(f'[ERROR] {attr}:', getattr(e, attr))
    sys.exit(1)
