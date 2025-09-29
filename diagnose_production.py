#!/usr/bin/env python3
"""
Script per diagnosticare il problema del database in produzione
"""
import json
import subprocess
import time

def test_database_health():
    """Testa la salute del database"""
    print("🔍 Testing Database Connection on Production...")
    print("="*50)
    
    # Test del nuovo endpoint di health check dettagliato
    health_url = "https://social-trends-api.onrender.com/health/detailed"
    
    try:
        result = subprocess.run([
            "curl", "-s", health_url
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            try:
                health_data = json.loads(result.stdout)
                print("✅ Health check response:")
                print(json.dumps(health_data, indent=2))
                
                if health_data.get("database") == "connected":
                    print("\n✅ Database connection is OK")
                    return True
                else:
                    print(f"\n❌ Database issue: {health_data.get('database')}")
                    return False
                    
            except json.JSONDecodeError:
                print("❌ Invalid health check response:")
                print(result.stdout)
                return False
        else:
            print("❌ Health check request failed")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_database_function():
    """Testa direttamente una query di database"""
    print("\n🧪 Testing Database Function...")
    print("-"*30)
    
    # Possiamo provare con un endpoint che non richiede la funzione generate_api_key_v2
    # ma usi solo query base
    test_url = "https://social-trends-api.onrender.com/v1/auth/v2/keys/test@example.com"
    
    try:
        result = subprocess.run([
            "curl", "-s", test_url
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                print("📧 Email lookup test:")
                print(json.dumps(response, indent=2))
                
                # Se questo endpoint funziona, il database base è OK
                # Il problema è specifico alla funzione generate_api_key_v2
                if response.get("status") in ["not_found", "success"]:
                    print("\n✅ Basic database queries work")
                    print("❌ Issue is with generate_api_key_v2 function")
                    return "function_missing"
                else:
                    print("\n❌ Database queries failing")
                    return "database_error"
                    
            except json.JSONDecodeError:
                print("❌ Invalid response from email endpoint")
                return "unknown"
        else:
            print("❌ Email endpoint request failed")
            return "network_error"
            
    except Exception as e:
        print(f"❌ Database function test error: {str(e)}")
        return "unknown"

def suggest_solutions(problem_type):
    """Suggerisce soluzioni basate sul tipo di problema"""
    print("\n🛠️ Suggested Solutions:")
    print("="*30)
    
    if problem_type == "function_missing":
        print("The generate_api_key_v2 function is missing from the database.")
        print("\n📋 To fix this:")
        print("1. Connect to your Render PostgreSQL database")
        print("2. Run the SQL script to create the missing function")
        print("3. Ensure the pgcrypto extension is installed")
        print("\n💡 SQL commands needed:")
        print("   CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        print("   -- Then run your generate_api_key_v2 function script")
        
    elif problem_type == "database_error":
        print("Basic database connection is failing.")
        print("\n📋 To fix this:")
        print("1. Check DATABASE_URL environment variable on Render")
        print("2. Verify PostgreSQL service is running")
        print("3. Check database credentials")
        
    elif problem_type == "network_error":
        print("Network connectivity issues.")
        print("\n📋 To check:")
        print("1. Verify Render service is running")
        print("2. Check service logs for errors")
        print("3. Ensure no firewall blocking connections")
        
    else:
        print("Unknown issue - check Render logs for more details")

def main():
    print("🚨 Social Trends API - Production Database Diagnostic")
    print("="*60)
    
    # Step 1: Test basic health
    db_healthy = test_database_health()
    
    # Step 2: Test database functions
    problem_type = test_database_function()
    
    # Step 3: Provide solutions
    suggest_solutions(problem_type)
    
    print("\n" + "="*60)
    print("🔍 Diagnostic completed")
    print("\n📋 Next steps:")
    print("   1. Check Render service logs")
    print("   2. Verify database setup")
    print("   3. Run missing SQL functions if needed")

if __name__ == "__main__":
    main()