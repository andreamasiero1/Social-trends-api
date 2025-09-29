#!/usr/bin/env python3
"""
Test API registration senza problemi di terminale
"""
import requests
import json

def test_registration():
    """Testa la registrazione API"""
    
    url = "http://localhost:8000/v1/auth/v2/register"
    headers = {"Content-Type": "application/json"}
    data = {"email": "test123@example.com", "tier": "free"}
    
    print("🧪 TESTING API REGISTRATION")
    print("=" * 40)
    print(f"URL: {url}")
    print(f"Data: {data}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("\n🎯 REGISTRATION SUCCESS!")
            if "verification_sent_to" in response_data:
                print(f"📧 Email sent to: {response_data['verification_sent_to']}")
            print("Check server logs for the verification link!")
        else:
            print(f"\n❌ Registration failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_registration()