#!/usr/bin/env python3
"""
Test connessione database con asyncpg (come fa l'app)
"""
import asyncio
import os
from api.core.config import settings

async def test_database_connection():
    """Testa la connessione al database usando asyncpg"""
    try:
        import asyncpg
        
        print("🔍 TESTING DATABASE CONNECTION")
        print("=" * 50)
        
        # Mostra URL configurato
        print(f"DATABASE_URL from config: {settings.DATABASE_URL}")
        print()
        
        # Tenta connessione
        print("Attempting connection...")
        conn = await asyncpg.connect(settings.DATABASE_URL)
        
        # Test query
        version = await conn.fetchval("SELECT version();")
        print("✅ CONNECTION SUCCESSFUL!")
        print(f"PostgreSQL Version: {version[:60]}...")
        
        # Test tabelle
        tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        print(f"\nTables found: {len(tables)}")
        for table in tables:
            print(f"  - {table['tablename']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ CONNECTION FAILED!")
        print(f"Error: {type(e).__name__}: {e}")
        
        if "role" in str(e) and "does not exist" in str(e):
            print("\n💡 DIAGNOSI: L'app sta usando credenziali sbagliate")
            print("L'errore 'role does not exist' indica che:")
            print("1. L'app non sta leggendo DATABASE_URL dal .env")
            print("2. Oppure sta usando le vecchie variabili POSTGRES_*")
        
        return False

if __name__ == "__main__":
    asyncio.run(test_database_connection())