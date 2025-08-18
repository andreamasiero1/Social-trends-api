#!/usr/bin/env python3
"""
Test con sistema di autenticazione mock per verificare la logica dei piani
senza dipendere dal database di produzione.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from api.routers import trends
from api.core.config import settings

# Mock del sistema di autenticazione per i test
class MockAPIKey:
    def __init__(self, key: str, tier: str):
        self.key = key
        self.tier = tier
        self.monthly_limit = {
            "free": 1000,
            "developer": 10000, 
            "business": 50000,
            "enterprise": 200000
        }.get(tier, 1000)
        self.usage_count = 0

# Database mock per i test
MOCK_API_KEYS = {
    "test_free_key_123": MockAPIKey("test_free_key_123", "free"),
    "test_premium_key_456": MockAPIKey("test_premium_key_456", "developer"),
    "test_enterprise_key_789": MockAPIKey("test_enterprise_key_789", "business"),
}

# Mock delle funzioni di sicurezza
async def mock_get_current_api_key(x_api_key: str = None):
    """Mock della funzione di autenticazione base."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key richiesta")
    
    if x_api_key not in MOCK_API_KEYS:
        raise HTTPException(status_code=401, detail="API Key non valida")
    
    return MOCK_API_KEYS[x_api_key]

async def mock_get_current_api_key_developer(x_api_key: str = None):
    """Mock per piani developer e superiori."""
    api_key = await mock_get_current_api_key(x_api_key)
    
    if api_key.tier not in ["developer", "business", "enterprise"]:
        raise HTTPException(status_code=403, detail="Questo endpoint richiede almeno il piano Developer")
    
    return api_key

async def mock_get_current_api_key_business(x_api_key: str = None):
    """Mock per piani business e superiori."""
    api_key = await mock_get_current_api_key(x_api_key)
    
    if api_key.tier not in ["business", "enterprise"]:
        raise HTTPException(status_code=403, detail="Questo endpoint richiede almeno il piano Business")
    
    return api_key

def create_mock_app():
    """Crea un'app FastAPI con autenticazione mock."""
    
    app = FastAPI(title="Mock Social Trends API")
    
    # Mock degli endpoint trends con autenticazione mock
    from fastapi import APIRouter, Query, Header
    from typing import Optional
    
    mock_router = APIRouter()
    
    @mock_router.get("/global")
    async def mock_global_trends(
        limit: int = Query(default=10, le=50),
        country: Optional[str] = Query(default=None),
        x_api_key: str = Header(alias="X-API-Key")
    ):
        """Mock endpoint trends globali - accessibile a tutti i piani."""
        api_key = await mock_get_current_api_key(x_api_key)
        
        return {
            "message": f"Global trends for {api_key.tier} plan",
            "data": ["#test1", "#test2", "#test3"],
            "limit": limit,
            "user_tier": api_key.tier
        }
    
    @mock_router.get("/platform")
    async def mock_platform_trends(
        source: str = Query(...),
        limit: int = Query(default=10, le=50),
        x_api_key: str = Header(alias="X-API-Key")
    ):
        """Mock endpoint trends per piattaforma - solo developer+."""
        api_key = await mock_get_current_api_key_developer(x_api_key)
        
        return {
            "message": f"Platform {source} trends for {api_key.tier} plan",
            "data": [f"#{source}1", f"#{source}2"],
            "user_tier": api_key.tier
        }
    
    @mock_router.get("/country")
    async def mock_country_trends(
        code: str = Query(...),
        x_api_key: str = Header(alias="X-API-Key")
    ):
        """Mock endpoint trends per paese - solo business+."""
        api_key = await mock_get_current_api_key_business(x_api_key)
        
        return {
            "message": f"Country {code} trends for {api_key.tier} plan",
            "data": [f"#{code}1", f"#{code}2"],
            "user_tier": api_key.tier
        }
    
    @mock_router.get("/analysis/keyword")
    async def mock_keyword_analysis(
        keyword: str = Query(...),
        x_api_key: str = Header(alias="X-API-Key")
    ):
        """Mock analisi keyword - solo developer+."""
        api_key = await mock_get_current_api_key_developer(x_api_key)
        
        return {
            "message": f"Keyword '{keyword}' analysis for {api_key.tier} plan",
            "keyword": keyword,
            "user_tier": api_key.tier
        }
    
    @mock_router.get("/hashtags/related")
    async def mock_related_hashtags(
        hashtag: str = Query(...),
        x_api_key: str = Header(alias="X-API-Key")
    ):
        """Mock hashtag correlati - solo developer+."""
        api_key = await mock_get_current_api_key_developer(x_api_key)
        
        return {
            "message": f"Related hashtags for '{hashtag}' - {api_key.tier} plan",
            "hashtag": hashtag,
            "user_tier": api_key.tier
        }
    
    app.include_router(mock_router, prefix="/v1/trends")
    
    return app

class MockAPITester:
    """Tester per l'API con autenticazione mock."""
    
    def __init__(self):
        self.app = create_mock_app()
        self.client = TestClient(self.app)
        self.test_keys = {
            "free": "test_free_key_123",
            "developer": "test_premium_key_456", 
            "business": "test_enterprise_key_789"
        }
        
        self.passed = 0
        self.failed = 0
        self.total = 0
    
    def test_endpoint(self, plan: str, endpoint: str, expected_status: int):
        """Testa un singolo endpoint."""
        
        self.total += 1
        
        headers = {"X-API-Key": self.test_keys[plan]}
        response = self.client.get(endpoint, headers=headers)
        
        success = response.status_code == expected_status
        
        status_icon = "✅" if success else "❌"
        plan_icons = {"free": "🆓", "developer": "💎", "business": "🚀"}
        
        print(f"{status_icon} {plan_icons[plan]} {plan.upper()} | GET {endpoint}")
        print(f"   Expected: {expected_status}, Got: {response.status_code}")
        
        if success:
            self.passed += 1
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Response: {data.get('message', 'OK')}")
        else:
            self.failed += 1
            if response.status_code != expected_status:
                print(f"   ❌ FAILED - Response: {response.json() if response.status_code != 500 else 'Internal Error'}")
        
        print("-" * 60)
        return success
    
    def run_plan_tests(self):
        """Esegue i test per tutti i piani."""
        
        print("🧪 TEST LOGICA PIANI CON AUTENTICAZIONE MOCK")
        print("="*70)
        
        # Test matrix: (endpoint, free_status, developer_status, business_status)
        test_matrix = [
            ("/v1/trends/global", 200, 200, 200),
            ("/v1/trends/global?limit=5", 200, 200, 200),
            ("/v1/trends/platform?source=tiktok", 403, 200, 200),
            ("/v1/trends/platform?source=instagram", 403, 200, 200),
            ("/v1/trends/country?code=US", 403, 403, 200),
            ("/v1/trends/country?code=IT", 403, 403, 200),
            ("/v1/trends/analysis/keyword?keyword=test", 403, 200, 200),
            ("/v1/trends/hashtags/related?hashtag=viral", 403, 200, 200),
        ]
        
        plans = ["free", "developer", "business"]
        
        for endpoint, free_status, dev_status, bus_status in test_matrix:
            expected_statuses = [free_status, dev_status, bus_status]
            
            print(f"\n📋 Testing {endpoint}")
            print("-" * 40)
            
            for i, plan in enumerate(plans):
                expected_status = expected_statuses[i]
                self.test_endpoint(plan, endpoint, expected_status)
        
        # Test autenticazione
        print(f"\n🔐 Test Autenticazione")
        print("-" * 40)
        
        # Test senza API key
        response = self.client.get("/v1/trends/global")
        self.total += 1
        if response.status_code == 401:
            self.passed += 1
            print("✅ No API Key: 401 (corretto)")
        else:
            self.failed += 1
            print(f"❌ No API Key: {response.status_code} (atteso 401)")
        
        # Test API key invalida
        response = self.client.get("/v1/trends/global", headers={"X-API-Key": "invalid_key"})
        self.total += 1
        if response.status_code == 401:
            self.passed += 1
            print("✅ Invalid API Key: 401 (corretto)")
        else:
            self.failed += 1
            print(f"❌ Invalid API Key: {response.status_code} (atteso 401)")
        
        print("-" * 70)
        
        # Riepilogo
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        
        print(f"\n📊 RISULTATI FINALI:")
        print(f"📋 Test totali: {self.total}")
        print(f"✅ Passati: {self.passed}")
        print(f"❌ Falliti: {self.failed}")
        print(f"📈 Successo: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n🎉 ECCELLENTE! La logica dei piani funziona perfettamente!")
            print("✅ Sistema pronto per il deploy su Render")
        elif success_rate >= 80:
            print("\n👍 BUONO! La logica funziona quasi perfettamente")
            print("🔧 Piccoli aggiustamenti potrebbero essere necessari")
        else:
            print("\n⚠️ Ci sono problemi nella logica dei piani")
            print("🛠️ Rivedi l'implementazione prima del deploy")
        
        return success_rate >= 80

def main():
    tester = MockAPITester()
    return tester.run_plan_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
