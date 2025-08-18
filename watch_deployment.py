#!/usr/bin/env python3
"""
Monitoraggio continuo del deployment Social Trends API
Controlla ogni 2 minuti se il deployment è completato
"""

import time
import requests
import json
from datetime import datetime
import sys

def test_new_endpoints(base_url="https://social-trends-api.onrender.com"):
    """Testa se i nuovi endpoint sono disponibili"""
    
    endpoints_to_test = [
        "/api/v2/auth/register",
        "/api/v2/auth/my-account", 
        "/api/v2/auth/verify-email",
        "/api/v2/auth/rapidapi/provision"
    ]
    
    available_endpoints = []
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            # 404 = endpoint non esiste, 405/422/401 = endpoint esiste ma metodo/dati sbagliati
            if response.status_code != 404:
                available_endpoints.append(endpoint)
        except:
            pass
    
    return available_endpoints

def check_deployment_status():
    """Controlla se il deployment è completato"""
    
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Controllo deployment...")
    
    try:
        # Test API base
        response = requests.get("https://social-trends-api.onrender.com/", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API non disponibile (status: {response.status_code})")
            return False
            
        # Test nuovi endpoint
        available = test_new_endpoints()
        
        if len(available) >= 3:  # Almeno 3 dei 4 endpoint disponibili
            print(f"✅ DEPLOYMENT COMPLETATO! Endpoint disponibili: {len(available)}/4")
            for endpoint in available:
                print(f"   ✓ {endpoint}")
            return True
        else:
            print(f"🔄 Deployment in corso... Endpoint disponibili: {len(available)}/4")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - servizio probabilmente in deployment")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 Connessione fallita - servizio non raggiungibile")
        return False
    except Exception as e:
        print(f"❌ Errore: {str(e)}")
        return False

def main():
    """Monitoraggio continuo"""
    
    print("🚀 MONITORAGGIO CONTINUO DEPLOYMENT")
    print("=" * 50)
    print("📡 URL: https://social-trends-api.onrender.com")
    print("⏹️  Premi Ctrl+C per fermare")
    print()
    
    max_checks = 30  # 30 controlli = 1 ora di monitoraggio
    check_count = 0
    
    try:
        while check_count < max_checks:
            deployment_ready = check_deployment_status()
            
            if deployment_ready:
                print("\n🎉 DEPLOYMENT COMPLETATO CON SUCCESSO!")
                print("\n🚀 PROSSIMI PASSI:")
                print("1. Configurare DATABASE_URL per produzione")
                print("2. Eseguire: python scripts/upgrade_database.py") 
                print("3. Testare tutti gli endpoint")
                print("4. Notificare utenti esistenti")
                print("\n📚 Documentazione aggiornata: https://social-trends-api.onrender.com/docs")
                break
            
            check_count += 1
            
            if check_count < max_checks:
                print(f"⏳ Prossimo controllo tra 2 minuti... ({check_count}/{max_checks})")
                time.sleep(120)  # 2 minuti
            
        if check_count >= max_checks:
            print(f"\n⚠️  Raggiunto limite controlli ({max_checks})")
            print("🔧 Il deployment potrebbe richiedere più tempo del previsto")
            print("📞 Controlla manualmente su: https://dashboard.render.com")
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoraggio interrotto dall'utente")
        print("📊 Per controllare manualmente:")
        print("   python monitor_deployment.py")

if __name__ == "__main__":
    main()
