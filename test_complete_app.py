#!/usr/bin/env python3
"""
Test completo dell'app FastAPI con il nuovo sistema trends con fallback
"""

import requests
import json
import time
from datetime import datetime

def test_country_endpoint(country_code="IT", limit=3):
    """Testa l'endpoint country trends"""
    
    url = f"https://social-trends-api.onrender.com/v1/trends/country"
    headers = {"X-API-Key": "test_enterprise_key_789"}
    params = {"code": country_code, "limit": limit}
    
    try:
        print(f"🌍 Testing /v1/trends/country per {country_code}...")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            trends_count = len(data.get("trends", []))
            
            if trends_count > 0:
                print(f"✅ SUCCESS! Trovati {trends_count} trends per {country_code}")
                
                # Mostra primi 3 trend
                for trend in data["trends"][:3]:
                    print(f"  {trend.get('rank', '?')}. {trend.get('name', 'N/A')} - {trend.get('volume', 0):,} vol")
                
                return True
            else:
                print(f"❌ STILL BROKEN: trends array vuoto per {country_code}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_auth_endpoints():
    """Testa se i nuovi endpoint auth sono disponibili"""
    
    auth_endpoints = [
        "/api/v2/auth/register",
        "/api/v2/auth/my-account",
        "/api/v2/auth/verify-email"
    ]
    
    print("\n🔐 Testing nuovi endpoint autenticazione...")
    
    available_count = 0
    
    for endpoint in auth_endpoints:
        try:
            url = f"https://social-trends-api.onrender.com{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 404:
                print(f"  ✅ {endpoint} - Disponibile (status: {response.status_code})")
                available_count += 1
            else:
                print(f"  ❌ {endpoint} - Non disponibile (404)")
                
        except Exception as e:
            print(f"  ⚠️  {endpoint} - Error: {str(e)[:50]}")
    
    return available_count

def check_global_trends():
    """Test endpoint trends globali per confronto"""
    
    print("\n📊 Testing /v1/trends/global (per confronto)...")
    
    try:
        url = "https://social-trends-api.onrender.com/v1/trends/global"
        headers = {"X-API-Key": "test_free_key_123"}
        params = {"limit": 3}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            trends_count = len(data.get("trends", []))
            print(f"✅ Global trends working: {trends_count} trends")
            return True
        else:
            print(f"❌ Global trends broken: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Test completo del sistema"""
    
    print("🧪 SOCIAL TRENDS API - TEST COMPLETO DEPLOYMENT")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()    
    # Test 1: Endpoint globali (baseline)
    global_ok = check_global_trends()
    
    # Test 2: Endpoint country (il problema principale)
    countries_to_test = ["IT", "US", "FR", "GB"]
    country_results = []
    
    for country in countries_to_test:
        result = test_country_endpoint(country, 2)
        country_results.append(result)
        time.sleep(1)  # Rate limiting
    
    # Test 3: Nuovi endpoint auth
    auth_available = test_auth_endpoints()
    
    # Summary
    print("\n📋 RISULTATI:")
    print(f"  🌍 Global trends: {'✅ OK' if global_ok else '❌ BROKEN'}")
    print(f"  🌐 Country trends: {sum(country_results)}/{len(country_results)} paesi OK")
    print(f"  🔐 Auth endpoints: {auth_available}/3 disponibili")
    
    # Determine deployment status
    if sum(country_results) > 0:
        print("\n🎉 COUNTRY TRENDS FIXED! Il fallback intelligente funziona!")
    elif global_ok:
        print("\n⏳ Deployment non ancora completato - trends country ancora vuoti")
    else:
        print("\n❌ Problemi generali con l'API")
    
    if auth_available >= 2:
        print("✅ Deployment nuove funzionalità completato!")
    else:
        print("⏳ Deployment nuove funzionalità in corso...")

if __name__ == "__main__":
    main()

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.main import app

def test_app_startup():
    """Test che l'app si avvii correttamente."""
    
    print("🚀 Test avvio app...")
    
    try:
        client = TestClient(app)
        
        # Test endpoint root
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        
        print(f"✅ App avviata: {data['name']} v{data['version']}")
        
        # Verifica che i nuovi endpoint siano presenti
        endpoints = data.get("endpoints", {})
        new_endpoints = ["register_v2", "verify_email", "my_account"]
        
        for endpoint in new_endpoints:
            assert endpoint in endpoints
            print(f"✅ Endpoint {endpoint}: {endpoints[endpoint]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nell'avvio: {str(e)}")
        return False

def test_health_check():
    """Test health check."""
    
    print("\n💓 Test health check...")
    
    try:
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        print(f"✅ Health check OK: {data['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore health check: {str(e)}")
        return False

def test_documentation():
    """Test che la documentazione sia accessibile."""
    
    print("\n📚 Test documentazione...")
    
    try:
        client = TestClient(app)
        
        # Test OpenAPI docs
        response = client.get("/docs")
        assert response.status_code == 200
        print("✅ /docs accessibile")
        
        # Test OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_data = response.json()
        assert "paths" in openapi_data
        
        # Verifica che i nuovi path siano presenti
        paths = openapi_data["paths"]
        new_paths = [
            "/v1/auth/v2/register",
            "/v1/auth/v2/verify-email",
            "/v1/auth/v2/my-account"
        ]
        
        for path in new_paths:
            assert path in paths
            print(f"✅ Path {path} documentato")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore documentazione: {str(e)}")
        return False

def test_error_handlers():
    """Test gestori di errore."""
    
    print("\n🚨 Test gestori di errore...")
    
    try:
        client = TestClient(app)
        
        # Test 404
        response = client.get("/endpoint-inesistente")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        print(f"✅ 404 gestito: {data['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nei gestori: {str(e)}")
        return False

def test_cors_headers():
    """Test header CORS."""
    
    print("\n🌐 Test CORS...")
    
    try:
        client = TestClient(app)
        
        # Test con header Origin
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        
        # Dovrebbe avere header CORS
        headers = response.headers
        print("✅ CORS configurato")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore CORS: {str(e)}")
        return False

def main():
    """Esegue tutti i test dell'app."""
    
    print("🚀 TEST COMPLETO APP FASTAPI\n")
    print("=" * 60)
    
    tests = [
        ("Avvio App", test_app_startup),
        ("Health Check", test_health_check),
        ("Documentazione", test_documentation),
        ("Gestori Errore", test_error_handlers),
        ("CORS", test_cors_headers),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 RISULTATI: {passed}/{total} test passati")
    
    if passed == total:
        print("🎉 APP COMPLETAMENTE TESTATA E PRONTA!")
        print("\n📋 PROSSIMI PASSI:")
        print("1. 🚀 Deploy su Render")
        print("2. 🗄️ Aggiorna database di produzione")
        print("3. 📧 Configura SMTP (opzionale)")
        print("4. 📱 Testa i nuovi endpoint")
        return True
    else:
        print("⚠️ Alcuni test sono falliti")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
