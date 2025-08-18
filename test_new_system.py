#!/usr/bin/env python3
"""
Test script per verificare i nuovi modelli e servizi senza toccare il database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models.trends import (
    UserRegistrationRequest, UserRegistrationResponse,
    RapidAPIKeyRequest, RapidAPIKeyResponse,
    EmailVerificationRequest, EmailVerificationResponse
)
import json

def test_models():
    """Test dei nuovi modelli Pydantic."""
    
    print("🧪 Test dei nuovi modelli Pydantic...")
    
    try:
        # Test UserRegistrationRequest
        reg_request = UserRegistrationRequest(
            email="test@example.com",
            tier="free"
        )
        print(f"✅ UserRegistrationRequest: {reg_request.email}, {reg_request.tier}")
        
        # Test UserRegistrationResponse
        reg_response = UserRegistrationResponse(
            message="Test message",
            requires_email_verification=True,
            verification_sent_to="test@example.com"
        )
        print(f"✅ UserRegistrationResponse: {reg_response.message}")
        
        # Test RapidAPIKeyRequest
        rapid_request = RapidAPIKeyRequest(
            email="rapid@example.com",
            tier="developer",
            rapidapi_user_id="rapid_123"
        )
        print(f"✅ RapidAPIKeyRequest: {rapid_request.email}, {rapid_request.rapidapi_user_id}")
        
        # Test RapidAPIKeyResponse
        rapid_response = RapidAPIKeyResponse(
            api_key="rapid_test_key_123",
            user_id=1,
            tier="developer",
            monthly_limit=10000
        )
        print(f"✅ RapidAPIKeyResponse: {rapid_response.api_key[:10]}...")
        
        print("\n🎉 Tutti i modelli sono validi!")
        return True
        
    except Exception as e:
        print(f"❌ Errore nei modelli: {str(e)}")
        return False

def test_email_service():
    """Test del servizio email (senza invio reale)."""
    
    print("\n📧 Test del servizio email...")
    
    try:
        # Importa il servizio email
        from api.services.email_service import EmailService
        
        # Verifica che la classe sia importabile
        print("✅ EmailService importato correttamente")
        
        # Verifica che i metodi esistano
        assert hasattr(EmailService, 'send_verification_email')
        assert hasattr(EmailService, 'verify_email_token')
        print("✅ Metodi EmailService disponibili")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nel servizio email: {str(e)}")
        return False

def test_config():
    """Test della configurazione aggiornata."""
    
    print("\n⚙️ Test della configurazione...")
    
    try:
        from api.core.config import settings
        
        # Verifica che le nuove configurazioni SMTP esistano
        smtp_configs = [
            'SMTP_SERVER', 'SMTP_PORT', 'SMTP_USE_TLS', 
            'SMTP_USERNAME', 'SMTP_PASSWORD', 'SMTP_FROM_EMAIL'
        ]
        
        for config in smtp_configs:
            assert hasattr(settings, config)
            print(f"✅ {config}: {getattr(settings, config)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nella configurazione: {str(e)}")
        return False

def test_json_serialization():
    """Test serializzazione JSON dei nuovi modelli."""
    
    print("\n📄 Test serializzazione JSON...")
    
    try:
        # Test serializzazione UserRegistrationResponse
        response = UserRegistrationResponse(
            message="Registrazione completata!",
            requires_email_verification=True,
            verification_sent_to="user@example.com"
        )
        
        json_data = response.model_dump()
        json_str = json.dumps(json_data, default=str)
        
        print(f"✅ JSON serializzato: {json_str}")
        
        # Test deserializzazione
        parsed = json.loads(json_str)
        reconstructed = UserRegistrationResponse(**parsed)
        
        print(f"✅ JSON deserializzato correttamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nella serializzazione: {str(e)}")
        return False

def main():
    """Esegue tutti i test."""
    
    print("🚀 SOCIAL TRENDS API - Test Sistema Migliorato\n")
    print("=" * 60)
    
    tests = [
        ("Modelli Pydantic", test_models),
        ("Servizio Email", test_email_service),
        ("Configurazione", test_config),
        ("Serializzazione JSON", test_json_serialization),
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
        print("🎉 TUTTI I TEST SONO PASSATI!")
        print("✅ Il sistema è pronto per il deploy")
        return True
    else:
        print("⚠️ Alcuni test sono falliti")
        print("🔧 Risolvi gli errori prima del deploy")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
