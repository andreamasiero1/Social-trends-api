#!/usr/bin/env python3
"""
Verifica completa del funzionamento RapidAPI
"""

import requests
import json
from datetime import datetime

def test_rapidapi_endpoint(country_code, expected_min_volume=0):
    """Testa un endpoint RapidAPI per verificare che funzioni"""
    
    url = f"https://social-trends-api.onrender.com/v1/trends/country"
    headers = {"X-API-Key": "test_enterprise_key_789"}
    params = {"code": country_code, "limit": 3}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}"
        
        data = response.json()
        
        # Verifica struttura risposta
        required_fields = ["country", "last_updated", "trends"]
        for field in required_fields:
            if field not in data:
                return False, f"Campo mancante: {field}"
        
        # Verifica che trends non sia vuoto
        if len(data["trends"]) == 0:
            return False, "Array trends vuoto"
        
        # Verifica primo trend ha campi richiesti
        first_trend = data["trends"][0]
        trend_fields = ["rank", "name", "volume", "growth_percentage", "platforms"]
        for field in trend_fields:
            if field not in first_trend:
                return False, f"Campo trend mancante: {field}"
        
        # Verifica volume minimo
        if first_trend["volume"] < expected_min_volume:
            return False, f"Volume troppo basso: {first_trend['volume']}"
        
        return True, {
            "country": data["country"],
            "trends_count": len(data["trends"]),
            "top_trend": first_trend["name"],
            "volume": first_trend["volume"],
            "growth": first_trend["growth_percentage"]
        }
        
    except Exception as e:
        return False, f"Errore: {str(e)}"

def main():
    """Test completo funzionamento RapidAPI"""
    
    print("🧪 VERIFICA FUNZIONAMENTO RAPIDAPI")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test diversi paesi con aspettative di volume
    test_cases = [
        ("US", 500000, "🇺🇸 Stati Uniti (volume alto)"),
        ("IT", 100000, "🇮🇹 Italia (volume medio)"),  
        ("DE", 150000, "🇩🇪 Germania (volume medio-alto)"),
        ("SG", 20000, "🇸🇬 Singapore (volume basso)"),
        ("FR", 120000, "🇫🇷 Francia (volume medio)"),
        ("XX", 1000, "🌍 Paese inesistente (fallback)")
    ]
    
    results = []
    
    for country, min_vol, description in test_cases:
        print(f"{description}")
        
        success, result = test_rapidapi_endpoint(country, min_vol)
        
        if success:
            print(f"  ✅ PASS: {result['top_trend']} - {result['volume']:,} vol ({result['growth']:+.1f}%)")
            results.append(True)
        else:
            print(f"  ❌ FAIL: {result}")
            results.append(False)
        
        print()
    
    # Riassunto
    success_count = sum(results)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100
    
    print("📊 RISULTATI FINALI:")
    print(f"   ✅ Successi: {success_count}/{total_count}")
    print(f"   📈 Tasso successo: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 PERFETTO! RapidAPI funziona al 100%")
        print("✅ Gli utenti vedono sempre dati")
        print("✅ Volumi realistici per ogni paese")
        print("✅ Zero array vuoti")
        print("\n💡 OPZIONALE: Aggiorna docs RapidAPI per marketing")
    elif success_rate >= 80:
        print("\n✅ BUONO! RapidAPI funziona bene")
        print("⚠️  Alcuni test falliti - controlla dettagli sopra")
    else:
        print("\n❌ PROBLEMI! RapidAPI non funziona correttamente")
        print("🔧 Risolvi i problemi prima di procedere")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
