#!/usr/bin/env python3
"""
Script per testare la connessione al database di produzione su Render
e verificare che sia pronto per l'aggiornamento.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def test_render_database():
    """Testa la connessione al database di produzione."""
    
    print("🔄 CONNESSIONE AL DATABASE DI PRODUZIONE")
    print("="*60)
    
    # Prova a connettersi usando le variabili d'ambiente di Render
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL non configurato")
        print("📋 Per testare con il database di produzione:")
        print("1. Vai su Render.com")
        print("2. Apri il tuo database PostgreSQL")
        print("3. Copia 'Internal Database URL'")
        print("4. Esegui: export DATABASE_URL='your_url_here'")
        print("5. Riprova questo script")
        return False
    
    # Converti per asyncpg
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "")
        database_url = "postgresql://" + database_url
    
    try:
        print(f"🔗 Connessione a: {database_url[:30]}...")
        
        conn = await asyncpg.connect(database_url)
        print("✅ Connessione al database riuscita!")
        
        # Test query semplice
        result = await conn.fetchval("SELECT version()")
        print(f"📊 Database version: {result[:50]}...")
        
        # Controlla tabelle esistenti
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"\n📋 Tabelle esistenti ({len(tables)}):")
        for table in tables:
            print(f"  • {table['table_name']}")
        
        # Controlla se abbiamo già la tabella users
        has_users = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            )
        """)
        
        if has_users:
            print("\n✅ Tabella 'users' già esistente")
            
            # Conta utenti esistenti
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            print(f"👥 Utenti registrati: {user_count}")
        else:
            print("\n🆕 Tabella 'users' non esistente - sarà creata dall'aggiornamento")
        
        # Controlla API keys esistenti
        api_key_count = await conn.fetchval("SELECT COUNT(*) FROM api_keys")
        print(f"🔑 API keys esistenti: {api_key_count}")
        
        # Verifica le chiavi di test
        test_keys = await conn.fetch("""
            SELECT key, tier, user_email, created_at 
            FROM api_keys 
            WHERE key LIKE 'test_%' 
            ORDER BY created_at DESC
        """)
        
        if test_keys:
            print(f"\n🧪 Chiavi di test trovate ({len(test_keys)}):")
            for key in test_keys[:3]:  # Mostra solo le prime 3
                print(f"  • {key['key'][:15]}... ({key['tier']}) - {key['user_email']}")
        
        await conn.close()
        
        print("\n🎯 DATABASE PRONTO PER L'AGGIORNAMENTO!")
        return True
        
    except Exception as e:
        print(f"❌ Errore connessione database: {str(e)}")
        print("\n🔧 Possibili soluzioni:")
        print("1. Verifica che DATABASE_URL sia corretto")
        print("2. Controlla che il database sia attivo su Render")
        print("3. Verifica le credenziali di accesso")
        return False

def main():
    print("🚀 SOCIAL TRENDS API - TEST DATABASE PRODUZIONE")
    print("="*70)
    
    # Carica .env se esiste
    if os.path.exists('.env'):
        load_dotenv()
        print("📄 File .env caricato")
    
    success = asyncio.run(test_render_database())
    
    if success:
        print("\n✅ Tutto pronto per applicare l'aggiornamento database!")
        print("\n🚀 Prossimo passo: Esegui l'aggiornamento con:")
        print("   python scripts/upgrade_database.py")
    else:
        print("\n❌ Risolvi i problemi di connessione prima di procedere")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
