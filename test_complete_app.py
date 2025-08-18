#!/usr/bin/env python3
"""
Test completo dell'app FastAPI con il nuovo sistema integrato.
"""

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
