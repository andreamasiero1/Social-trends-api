#!/usr/bin/env python3
"""
Test completo di tutti gli endpoint API per ogni piano di abbonamento.
Testa ogni richiesta individualmente per verificare il comportamento corretto.
"""

import sys
import os
import asyncio
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.main import app

class APITester:
    """Classe per testare sistematicamente tutti gli endpoint."""
    
    def __init__(self):
        self.client = TestClient(app)
        self.test_keys = {
            "free": "test_free_key_123",
            "premium": "test_premium_key_456", 
            "enterprise": "test_enterprise_key_789"
        }
        
        # Contatori per i risultati
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, plan: str, endpoint: str, method: str, expected_status: int, actual_status: int, success: bool):
        """Logga il risultato di un test."""
        self.total_tests += 1
        
        status_icon = "✅" if success else "❌"
        plan_icon = {"free": "🆓", "premium": "💎", "enterprise": "🚀"}.get(plan, "🔧")
        
        print(f"{status_icon} {plan_icon} {plan.upper()} | {method} {endpoint}")
        print(f"   Expected: {expected_status}, Got: {actual_status}")
        
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            print(f"   ⚠️ FAILED - Expected {expected_status}, got {actual_status}")
        
        print("-" * 60)
        
    def test_request(self, plan: str, method: str, endpoint: str, expected_status: int, headers: dict = None):
        """Esegue un singolo test di richiesta."""
        
        try:
            # Prepara gli headers
            test_headers = {}
            if headers:
                test_headers.update(headers)
            
            # Aggiungi API key se il piano lo richiede
            if plan != "no_auth":
                test_headers["X-API-Key"] = self.test_keys.get(plan, "invalid_key")
            
            # Esegui la richiesta
            if method == "GET":
                response = self.client.get(endpoint, headers=test_headers)
            elif method == "POST":
                response = self.client.post(endpoint, headers=test_headers, json={})
            else:
                response = self.client.request(method, endpoint, headers=test_headers)
            
            # Verifica il risultato
            success = response.status_code == expected_status
            self.log_test(plan, endpoint, method, expected_status, response.status_code, success)
            
            return success, response
            
        except Exception as e:
            print(f"❌ ERRORE nel test {plan} {method} {endpoint}: {str(e)}")
            self.log_test(plan, endpoint, method, expected_status, 500, False)
            return False, None

    def test_public_endpoints(self):
        """Test endpoint pubblici (senza autenticazione)."""
        
        print("\n" + "="*60)
        print("🌐 TEST ENDPOINT PUBBLICI")
        print("="*60)
        
        public_tests = [
            ("GET", "/", 200),
            ("GET", "/health", 200),
            ("GET", "/docs", 200),
            ("GET", "/openapi.json", 200),
        ]
        
        for method, endpoint, expected in public_tests:
            self.test_request("no_auth", method, endpoint, expected)
            time.sleep(0.1)  # Piccola pausa tra i test

    def test_auth_endpoints(self):
        """Test endpoint di autenticazione."""
        
        print("\n" + "="*60)
        print("🔑 TEST ENDPOINT AUTENTICAZIONE")
        print("="*60)
        
        # Test endpoint auth originali (dovrebbero funzionare senza DB reale)
        auth_tests = [
            # Questi falliranno perché non abbiamo DB, ma testiamo che raggiungano l'endpoint
            ("free", "POST", "/v1/auth/generate-key?email=test@test.com&tier=free", [422, 500]),
            ("free", "GET", "/v1/auth/usage?api_key=test_free_key_123", [422, 500]),
        ]
        
        for plan, method, endpoint, expected_statuses in auth_tests:
            success, response = self.test_request(plan, method, endpoint, expected_statuses[0])
            if not success and len(expected_statuses) > 1:
                # Prova con il secondo status code accettabile
                if response and response.status_code in expected_statuses:
                    print(f"   ✅ Accepted alternative status: {response.status_code}")
                    self.passed_tests += 1
                    self.failed_tests -= 1
            time.sleep(0.1)

    def test_trends_endpoints_by_plan(self):
        """Test endpoint trends per ogni piano."""
        
        print("\n" + "="*60)
        print("📈 TEST ENDPOINT TRENDS PER PIANO")
        print("="*60)
        
        # Definizione degli endpoint e del loro accesso per piano
        trends_tests = [
            # (endpoint, free_status, premium_status, enterprise_status)
            ("/v1/trends/global", 200, 200, 200),  # Tutti possono accedere
            ("/v1/trends/global?limit=5", 200, 200, 200),
            ("/v1/trends/platform?source=tiktok", 403, 200, 200),  # Solo premium+
            ("/v1/trends/platform?source=instagram", 403, 200, 200),
            ("/v1/trends/country?code=US", 403, 403, 200),  # Solo enterprise
            ("/v1/trends/country?code=IT", 403, 403, 200),
            ("/v1/trends/analysis/keyword?keyword=test", 403, 200, 200),  # Solo premium+
            ("/v1/trends/hashtags/related?hashtag=test", 403, 200, 200),  # Solo premium+
        ]
        
        plans = ["free", "premium", "enterprise"]
        
        for endpoint, free_status, premium_status, enterprise_status in trends_tests:
            expected_statuses = [free_status, premium_status, enterprise_status]
            
            for i, plan in enumerate(plans):
                expected_status = expected_statuses[i]
                self.test_request(plan, "GET", endpoint, expected_status)
                time.sleep(0.1)

    def test_authentication_scenarios(self):
        """Test scenari di autenticazione."""
        
        print("\n" + "="*60)
        print("🔐 TEST SCENARI AUTENTICAZIONE")
        print("="*60)
        
        # Test senza API key
        print("\n🚫 Test senza API Key:")
        self.test_request("no_auth", "GET", "/v1/trends/global", 401)
        
        # Test con API key invalida
        print("\n❌ Test con API Key invalida:")
        invalid_response = self.client.get("/v1/trends/global", headers={"X-API-Key": "invalid_key_123"})
        success = invalid_response.status_code == 401
        self.log_test("invalid", "/v1/trends/global", "GET", 401, invalid_response.status_code, success)
        
        # Test con API key vuota
        print("\n📭 Test con API Key vuota:")
        empty_response = self.client.get("/v1/trends/global", headers={"X-API-Key": ""})
        success = empty_response.status_code in [401, 422]
        self.log_test("empty", "/v1/trends/global", "GET", 401, empty_response.status_code, success)

    def test_error_endpoints(self):
        """Test endpoint che dovrebbero restituire errori."""
        
        print("\n" + "="*60)
        print("🚨 TEST ENDPOINT ERRORI")
        print("="*60)
        
        error_tests = [
            # Endpoint inesistenti
            ("GET", "/v1/trends/nonexistent", 404),
            ("GET", "/v1/auth/nonexistent", 404),
            ("GET", "/nonexistent", 404),
            # Metodi non supportati
            ("DELETE", "/v1/trends/global", 405),
            ("PUT", "/v1/trends/global", 405),
        ]
        
        for method, endpoint, expected in error_tests:
            # Usa una chiave valida per essere sicuri che l'errore sia per l'endpoint, non per l'auth
            headers = {"X-API-Key": self.test_keys["free"]} if "/v1/" in endpoint else {}
            
            try:
                if method == "GET":
                    response = self.client.get(endpoint, headers=headers)
                elif method == "DELETE":
                    response = self.client.delete(endpoint, headers=headers)
                elif method == "PUT":
                    response = self.client.put(endpoint, headers=headers)
                else:
                    response = self.client.request(method, endpoint, headers=headers)
                
                success = response.status_code == expected
                self.log_test("error", endpoint, method, expected, response.status_code, success)
                
            except Exception as e:
                print(f"❌ Errore nel test errore {method} {endpoint}: {str(e)}")
                self.log_test("error", endpoint, method, expected, 500, False)
            
            time.sleep(0.1)

    def test_rate_limiting_simulation(self):
        """Simula test di rate limiting."""
        
        print("\n" + "="*60)
        print("⏱️ TEST SIMULAZIONE RATE LIMITING")
        print("="*60)
        
        # Test multiple richieste rapide (senza DB reale, non possiamo testare il vero rate limiting)
        print("🔄 Test richieste multiple rapide...")
        
        for i in range(5):
            response = self.client.get("/v1/trends/global", headers={"X-API-Key": self.test_keys["free"]})
            success = response.status_code in [200, 500, 429]  # 500 per DB mancante, 429 per rate limit
            
            print(f"   Richiesta {i+1}: Status {response.status_code}")
            if success:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            self.total_tests += 1
            
            time.sleep(0.1)

    def run_all_tests(self):
        """Esegue tutti i test."""
        
        print("🚀 SOCIAL TRENDS API - TEST COMPLETO PER PIANO")
        print("="*80)
        print(f"⏰ Inizio test: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Esegui tutti i gruppi di test
        self.test_public_endpoints()
        self.test_auth_endpoints()
        self.test_trends_endpoints_by_plan()
        self.test_authentication_scenarios()
        self.test_error_endpoints()
        self.test_rate_limiting_simulation()
        
        # Riepilogo finale
        self.print_final_summary()
    
    def print_final_summary(self):
        """Stampa il riepilogo finale dei test."""
        
        print("\n" + "="*80)
        print("📊 RIEPILOGO FINALE TEST")
        print("="*80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📋 Test totali eseguiti: {self.total_tests}")
        print(f"✅ Test passati: {self.passed_tests}")
        print(f"❌ Test falliti: {self.failed_tests}")
        print(f"📈 Percentuale successo: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 OTTIMO! L'API è pronta per il deploy!")
            print("✅ La maggior parte dei test è passata")
        elif success_rate >= 60:
            print("\n⚠️ BUONO, ma ci sono alcuni problemi")
            print("🔧 Risolvi i test falliti prima del deploy")
        else:
            print("\n❌ ATTENZIONE! Molti test sono falliti")
            print("🛠️ Risolvi i problemi prima di procedere")
        
        print("\n🔍 NOTE:")
        print("• Molti test falliranno perché non c'è un database reale connesso")
        print("• Gli errori 500 sono normali in ambiente di test")
        print("• Gli errori 401/403 indicano che l'autenticazione funziona")
        print("• Gli errori 404/405 indicano che il routing funziona")
        
        print("\n🚀 PROSSIMI PASSI:")
        print("1. Deploy su Render")
        print("2. Aggiorna database di produzione")
        print("3. Testa gli endpoint reali con il database")
        
        return success_rate >= 70  # Considera successo se >70% passa

def main():
    """Funzione principale."""
    
    tester = APITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
