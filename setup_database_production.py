#!/usr/bin/env python3
"""
Script per configurare automaticamente il database di produzione
Esegue setup_production_db.sql nel database PostgreSQL di Render
"""
import asyncio
import asyncpg
import os
import sys
from pathlib import Path

async def setup_production_database():
    """Configura il database di produzione eseguendo lo script SQL"""
    
    print("🚀 Social Trends API - Database Production Setup")
    print("="*60)
    
    # URL del database - prendi dalla variabile d'ambiente o chiedi all'utente
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL non trovato nelle variabili d'ambiente")
        print("\n📋 Come ottenere il DATABASE_URL da Render:")
        print("   1. Vai su https://dashboard.render.com")
        print("   2. Clicca sul tuo database PostgreSQL")
        print("   3. Nella sezione 'Connections', copia 'External Database URL'")
        print("   4. Deve essere simile a: postgresql://user:pass@dpg-xyz.oregon-postgres.render.com/dbname")
        print()
        
        database_url = input("🔗 Incolla qui il DATABASE_URL: ").strip()
        
        if not database_url:
            print("❌ DATABASE_URL richiesto per continuare")
            return False
    
    # Converti per asyncpg se necessario
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql://", 1)
    
    print(f"🔗 Connessione a: {database_url[:30]}...")
    
    try:
        # Connetti al database
        print("🔌 Connecting to database...")
        conn = await asyncpg.connect(database_url)
        
        # Leggi lo script SQL
        script_path = Path(__file__).parent / "setup_production_db.sql"
        if not script_path.exists():
            print(f"❌ Script SQL non trovato: {script_path}")
            return False
            
        print("📄 Reading SQL script...")
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("⚡ Executing SQL script...")
        
        # Esegui lo script SQL
        await conn.execute(sql_script)
        
        print("✅ Script SQL eseguito con successo!")
        
        # Test la funzione generate_api_key_v2
        print("\n🧪 Testing generate_api_key_v2 function...")
        test_result = await conn.fetchval(
            "SELECT generate_api_key_v2($1, $2, $3)",
            "test_setup@example.com", "free", "setup_test"
        )
        
        print(f"📋 Test result: {test_result}")
        
        if test_result and '"success":true' in str(test_result):
            print("✅ Function generate_api_key_v2 is working!")
        else:
            print("⚠️ Function test returned unexpected result")
        
        # Chiudi connessione
        await conn.close()
        
        print("\n🎉 Database setup completed successfully!")
        print("🚀 Your API should now work on Render")
        
        return True
        
    except asyncpg.InvalidCatalogNameError as e:
        print(f"❌ Database connection failed - invalid database name: {e}")
        print("💡 Check that the database name in the URL is correct")
        return False
        
    except asyncpg.InvalidPasswordError as e:
        print(f"❌ Database connection failed - invalid credentials: {e}")
        print("💡 Check username and password in the DATABASE_URL")
        return False
        
    except asyncpg.ConnectionDoesNotExistError as e:
        print(f"❌ Database connection failed - server not found: {e}")
        print("💡 Check the server address in the DATABASE_URL")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

async def test_api_after_setup():
    """Testa l'API dopo il setup del database"""
    import subprocess
    import json
    import time
    
    print("\n🧪 Testing API after database setup...")
    print("-"*40)
    
    # Aspetta un po' per il deployment
    print("⏱️ Waiting for deployment to complete...")
    time.sleep(5)
    
    test_data = {
        "email": f"post_setup_test_{int(time.time())}@example.com",
        "tier": "free"
    }
    
    try:
        result = subprocess.run([
            "curl", "-s", "-X", "POST",
            "https://social-trends-api.onrender.com/v1/auth/v2/register",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(test_data)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                print("📋 API Test Response:")
                print(json.dumps(response, indent=2))
                
                if response.get("status") == "success":
                    print("\n🎉 SUCCESS! API is working correctly!")
                    api_key = response.get("api_key", "")
                    print(f"🔑 Generated API Key: {api_key[:15]}...")
                else:
                    print(f"\n⚠️ API returned error: {response.get('message', 'Unknown error')}")
                    
            except json.JSONDecodeError:
                print("❌ Invalid JSON response from API")
                print(f"Raw response: {result.stdout}")
        else:
            print("❌ API test request failed")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ API test error: {str(e)}")

def main():
    """Main function"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        sys.exit(1)
    
    try:
        # Setup database
        success = asyncio.run(setup_production_database())
        
        if success:
            # Test API
            asyncio.run(test_api_after_setup())
        else:
            print("\n❌ Database setup failed - cannot test API")
            
    except KeyboardInterrupt:
        print("\n⏹️ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")

if __name__ == "__main__":
    main()