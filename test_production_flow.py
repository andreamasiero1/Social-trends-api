#!/usr/bin/env python3
"""
Test completo del processo di registrazione e verifica su Render
"""
import requests
import json
import re
import time

def test_production_registration():
    """Testa la registrazione completa su Render"""
    
    BASE_URL = "https://social-trends-api.onrender.com"
    test_email = f"test{int(time.time())}@example.com"
    
    print("🚀 TESTING PRODUCTION REGISTRATION")
    print("=" * 50)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Email: {test_email}")
    print()
    
    # Step 1: Registrazione
    print("📝 STEP 1: Registrazione utente")
    print("-" * 30)
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/auth/v2/register",
            headers={"Content-Type": "application/json"},
            json={"email": test_email, "tier": "free"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            print("❌ Registration failed!")
            return False
            
        data = response.json()
        if not data.get("requires_email_verification"):
            print("❌ Expected email verification requirement!")
            return False
            
        print("✅ Registration successful!")
        print(f"📧 Verification email should be sent to: {data.get('verification_sent_to')}")
        
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("📧 STEP 2: Come trovare il link di verifica")
    print("-" * 30)
    print("Il link di verifica è stato inviato ma ci sono 3 modi per ottenerlo:")
    print()
    print("METODO 1 - Log del servizio su Render:")
    print("1. Vai su render.com")
    print("2. Apri il tuo Web Service")
    print("3. Clicca su 'Logs'")
    print("4. Cerca una riga tipo:")
    print(f"   📧 EMAIL DI VERIFICA PER {test_email}:")
    print("   🔗 Link: https://social-trends-api.onrender.com/v1/auth/v2/verify-email?token=...")
    print()
    print("METODO 2 - Query diretta al database:")
    print("(Se hai accesso al database)")
    print()
    print("METODO 3 - Email reale (se hai configurato SMTP):")
    print("Controlla la casella email")
    
    print("\n" + "=" * 50)
    print("🔗 STEP 3: Test del link di verifica")
    print("-" * 30)
    print("Una volta ottenuto il token, testalo con:")
    print(f"curl \"{BASE_URL}/v1/auth/v2/verify-email?token=IL_TUO_TOKEN\"")
    print()
    print("Risposta attesa:")
    print('{"message":"✅ Email verificata con successo! La tua API key è: api_xxx","api_key":"api_xxx"}')
    
    print("\n" + "=" * 50)
    print("🧪 STEP 4: Test API key")
    print("-" * 30)
    print("Con l'API key ottenuta, testa gli endpoint:")
    print(f"curl -H \"X-API-Key: api_xxx\" \"{BASE_URL}/v1/trends/global\"")
    
    return True

def get_token_from_database():
    """Aiuto per recuperare il token dal database"""
    print("\n" + "=" * 50)
    print("📊 RECUPERO TOKEN DAL DATABASE")
    print("-" * 30)
    print("Se hai accesso al database, puoi recuperare l'ultimo token con:")
    print()
    
    db_query = """
    SELECT 
        u.email,
        ev.token,
        ev.created_at,
        ev.expires_at,
        CONCAT('https://social-trends-api.onrender.com/v1/auth/v2/verify-email?token=', ev.token) as verification_url
    FROM email_verifications ev
    JOIN users u ON ev.user_id = u.id
    WHERE ev.verified_at IS NULL 
    AND ev.expires_at > NOW()
    ORDER BY ev.created_at DESC
    LIMIT 5;
    """
    
    print("Query SQL:")
    print(db_query)
    print()
    print("Comando psql (sostituisci le credenziali):")
    print('psql "postgresql://user:pass@host:5432/db?sslmode=require" -c "QUERY_SOPRA"')

def test_verification_workflow():
    """Simula il workflow completo"""
    print("\n" + "=" * 60)
    print("📋 WORKFLOW COMPLETO DI VERIFICA")
    print("=" * 60)
    
    steps = [
        "1. 📝 Esegui registrazione con curl",
        "2. ✅ Verifica risposta 200 + requires_email_verification=true", 
        "3. 📋 Vai sui log di Render per trovare il link",
        "4. 🔗 Copia il token dal link mostrato nei log",
        "5. 🧪 Testa il link di verifica con curl",
        "6. 🔑 Ottieni l'API key dalla risposta",
        "7. 🚀 Testa l'API key sugli endpoint",
        "8. 🎉 Successo!"
    ]
    
    for step in steps:
        print(step)
    
    print("\n" + "⚠️  " + "IMPORTANTE" + " ⚠️")
    print("Se non vedi il link nei log, significa:")
    print("- Il database non è connesso correttamente")
    print("- Le variabili d'ambiente non sono configurate")
    print("- Il deploy non è andato a buon fine")

if __name__ == "__main__":
    test_production_registration()
    get_token_from_database()
    test_verification_workflow()
    
    print("\n" + "🎯 " + "PROSSIMI PASSI" + " 🎯")
    print("1. Esegui il comando di registrazione")
    print("2. Vai sui log di Render per il link")
    print("3. Testa il link di verifica")
    print("4. Usa l'API key ottenuta")