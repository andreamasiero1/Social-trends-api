#!/usr/bin/env python3
"""
Script per monitorare e gestire il deployment della Social Trends API
"""

import requests
import json
import time
from datetime import datetime
import os

def check_api_status(url="https://social-trends-api.onrender.com"):
    """Controlla lo stato dell'API deployata"""
    
    print(f"🔍 CONTROLLO API: {url}")
    print("="*60)
    
    try:
        # Test endpoint di salute
        response = requests.get(f"{url}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API ONLINE!")
            print(f"📊 Status: {data.get('status', 'N/A')}")
            print(f"🏷️  Version: {data.get('version', 'N/A')}")
            print(f"⏰ Timestamp: {data.get('timestamp', 'N/A')}")
            return True
        else:
            print(f"⚠️  Status Code: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️  TIMEOUT - Il servizio sta probabilmente ancora deployando...")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 CONNECTION ERROR - Servizio non ancora disponibile")
        return False
    except Exception as e:
        print(f"❌ Errore: {str(e)}")
        return False

def check_auth_endpoints(url="https://social-trends-api.onrender.com"):
    """Testa i nuovi endpoint di autenticazione"""
    
    print(f"\n🔐 TEST NUOVI ENDPOINT AUTH")
    print("="*60)
    
    try:
        # Test registrazione (deve fallire senza dati validi, ma endpoint deve esistere)
        response = requests.post(f"{url}/api/v2/auth/register", 
                               json={}, timeout=10)
        
        if response.status_code in [422, 400]:
            print("✅ Endpoint /api/v2/auth/register ATTIVO")
        else:
            print(f"⚠️  Endpoint register risponde con: {response.status_code}")
        
        # Test my-account (deve restituire 401 senza auth)
        response = requests.get(f"{url}/api/v2/auth/my-account", timeout=10)
        
        if response.status_code == 401:
            print("✅ Endpoint /api/v2/auth/my-account ATTIVO (401 corretto)")
        else:
            print(f"⚠️  Endpoint my-account risponde con: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ Errore test auth: {str(e)}")
        return False

def check_trends_endpoints(url="https://social-trends-api.onrender.com"):
    """Testa gli endpoint trends esistenti"""
    
    print(f"\n📈 TEST ENDPOINT TRENDS")
    print("="*60)
    
    try:
        # Test senza API key (deve dare 401)
        response = requests.get(f"{url}/api/trends/instagram", timeout=10)
        
        if response.status_code == 401:
            print("✅ Endpoint trends protetto correttamente (401)")
        else:
            print(f"⚠️  Endpoint trends risponde con: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ Errore test trends: {str(e)}")
        return False

def deployment_checklist():
    """Mostra la checklist del deployment"""
    
    print("\n📋 CHECKLIST DEPLOYMENT")
    print("="*60)
    
    checklist = [
        "✅ Codice pushato su GitHub",
        "🔄 Render deployment in corso...",
        "⏳ Database upgrade in attesa",
        "⏳ Test production endpoints",
        "⏳ Notifica utenti esistenti",
        "⏳ Documentazione API aggiornata"
    ]
    
    for item in checklist:
        print(f"  {item}")
    
    print("\n🚀 PROSSIMI PASSI:")
    print("1. Attendere completamento deployment Render")
    print("2. Configurare DATABASE_URL per produzione") 
    print("3. Eseguire scripts/upgrade_database.py")
    print("4. Testare tutti gli endpoint in produzione")
    print("5. Aggiornare documentazione OpenAPI")

def main():
    """Funzione principale"""
    
    print("🚀 SOCIAL TRENDS API - MONITORAGGIO DEPLOYMENT")
    print("="*70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check API status
    api_online = check_api_status()
    
    if api_online:
        # Test new endpoints
        check_auth_endpoints()
        check_trends_endpoints()
    else:
        print("\n⏱️  API non ancora online - deployment probabilmente in corso")
        print("🔄 Riprova tra qualche minuto...")
    
    # Show deployment checklist
    deployment_checklist()
    
    print(f"\n🔗 URL API: https://social-trends-api.onrender.com")
    print(f"📚 Docs: https://social-trends-api.onrender.com/docs")

if __name__ == "__main__":
    main()
