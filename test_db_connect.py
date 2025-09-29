import os, asyncio, asyncpg

# Legge variabile DATABASE_URL (versione asyncpg compatibile) oppure usa una di fallback
# Assicurati di esportare prima: export DB_DIAG_URL="postgresql://user:pass@host:5432/dbname?sslmode=require"
URI = os.getenv("DB_DIAG_URL") or "postgresql://social_trends_user:REPLACE_PASSWORD@dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com:5432/social_trends?sslmode=require"

async def main():
    print("== Test connessione asyncpg ==")
    print("URI (senza password):", URI.replace(os.getenv('DB_PASSWORD',''), '***'))
    try:
        conn = await asyncpg.connect(URI)
        ver = await conn.fetchval("SELECT version();")
        print("CONNESSIONE OK:", ver)
        await conn.close()
    except Exception as e:
        print("ERRORE:", repr(e))
        # Dettagli aggiuntivi utili
        if hasattr(e, 'args'):
            for i,a in enumerate(e.args):
                print(f"arg[{i}]=", a)

if __name__ == "__main__":
    asyncio.run(main())
