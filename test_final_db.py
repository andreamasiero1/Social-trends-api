#!/usr/bin/env python3
"""
Test finale connessione database
"""
import asyncio
import sys
import os

sys.path.append('/Users/andreamasiero/Documents/Social-trends-api')

async def main():
    print("🔍 FINAL DATABASE CONNECTION TEST")
    print("=" * 50)
    
    try:
        from api.core.config import settings
        print(f"✅ Configurazione caricata")
        print(f"Database URL: {settings.get_database_url()}")
        
        # Test connessione diretta asyncpg
        import asyncpg
        
        db_url = settings.get_database_url()
        # Converte per asyncpg
        if db_url.startswith("postgresql+asyncpg://"):
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        
        print(f"\nConnessione a: {db_url.split('@')[1]}")  # Nasconde credenziali
        
        conn = await asyncpg.connect(db_url)
        version = await conn.fetchval("SELECT version();")
        print(f"✅ CONNESSIONE RIUSCITA!")
        print(f"PostgreSQL: {version[:50]}...")
        
        # Test tabelle
        tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;")
        print(f"\n📊 Tabelle trovate: {len(tables)}")
        for table in tables:
            print(f"  - {table['tablename']}")
        
        # Test funzione generate_api_key_v2
        try:
            result = await conn.fetchval("SELECT generate_api_key_v2('test@example.com', 'free', 'direct')")
            print(f"\n✅ Funzione generate_api_key_v2 funziona")
        except Exception as e:
            print(f"\n❌ Funzione generate_api_key_v2: {e}")
            
        await conn.close()
        print(f"\n🎯 DATABASE READY!")
        
    except Exception as e:
        print(f"❌ ERRORE: {type(e).__name__}: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n✨ Tutto pronto per testare la registrazione!")
    else:
        print("\n❌ Ci sono ancora problemi da risolvere.")