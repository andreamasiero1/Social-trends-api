#!/usr/bin/env python3
"""
Test per verificare se l'API su Render può accedere alle funzioni del database
"""
import json
import subprocess

def test_api_database_access():
    """Testa se l'API può accedere alle funzioni del database"""
    print("🔍 Testing API database access on Render...")
    print("="*50)
    
    # Test 1: Health check dettagliato
    print("1️⃣ Detailed health check...")
    try:
        result = subprocess.run([
            "curl", "-s", "https://social-trends-api.onrender.com/health/detailed"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            health = json.loads(result.stdout)
            print(f"   Status: {health.get('status')}")
            print(f"   Database: {health.get('database')}")
        else:
            print("   ❌ Health check failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Prova endpoint che usa query semplice
    print("\n2️⃣ Testing simple database endpoint...")
    try:
        result = subprocess.run([
            "curl", "-s", "https://social-trends-api.onrender.com/v1/auth/v2/keys/nonexistent@test.com"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print(f"   Response: {response.get('status', 'unknown')}")
            if response.get("status") == "not_found":
                print("   ✅ Basic database queries work")
            else:
                print("   ❌ Unexpected response")
        else:
            print("   ❌ Request failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Prova con email già esistente (dovrebbe dare errore specifico)
    print("\n3️⃣ Testing with known existing email...")
    try:
        result = subprocess.run([
            "curl", "-s", "-X", "POST", 
            "https://social-trends-api.onrender.com/v1/auth/v2/register",
            "-H", "Content-Type: application/json",
            "-d", '{"email":"test_setup@example.com","tier":"free"}'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print(f"   Response: {response}")
            
            if "email_already_exists" in str(response) or "già registrata" in str(response):
                print("   ✅ Database function is accessible and working!")
            elif "funzione generate_api_key_v2 non disponibile" in str(response):
                print("   ❌ Function not accessible from API")
            else:
                print("   ❓ Unexpected response - need investigation")
        else:
            print("   ❌ Request failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_api_database_access()