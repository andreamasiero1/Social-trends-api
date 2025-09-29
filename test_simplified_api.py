#!/usr/bin/env python3
"""
Script per testare l'API semplificata
"""
import json
import subprocess
import time

def test_api():
    """Test dell'API semplificata senza dipendenze esterne"""
    
    # Dati del test
    test_data = {
        "email": f"test_simplified_{int(time.time())}@example.com",
        "tier": "free"
    }
    
    print("🧪 Testing Simplified Registration API...")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    print()
    
    # Comando curl per testare
    curl_cmd = [
        "curl",
        "-X", "POST",
        "http://127.0.0.1:8000/v1/auth/v2/register",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(test_data),
        "-s"  # silent mode
    ]
    
    try:
        # Esegui il comando
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            try:
                response_data = json.loads(result.stdout)
                print("✅ SUCCESS - API Response:")
                print(json.dumps(response_data, indent=2))
                
                # Verifica che la risposta contenga l'API key
                if response_data.get("status") == "success" and response_data.get("api_key"):
                    api_key = response_data["api_key"]
                    print(f"\n🔑 API Key generated: {api_key[:10]}...{api_key[-4:]}")
                    print(f"📧 Email: {response_data.get('email')}")
                    print(f"📊 Tier: {response_data.get('tier')}")
                    print(f"🎯 Monthly Limit: {response_data.get('monthly_limit')}")
                    
                    return True, api_key
                else:
                    print("❌ Missing API key in response")
                    return False, None
                    
            except json.JSONDecodeError:
                print("❌ Invalid JSON response:")
                print(result.stdout)
                return False, None
        else:
            print(f"❌ Curl failed with return code: {result.returncode}")
            print(f"Error: {result.stderr}")
            return False, None
            
    except subprocess.TimeoutExpired:
        print("❌ Request timeout - server might not be running")
        return False, None
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False, None

def test_duplicate_registration():
    """Test registrazione con email duplicata"""
    print("\n" + "="*50)
    print("🔄 Testing duplicate email registration...")
    
    # Usa una email fissa per testare la duplicazione
    test_data = {
        "email": "duplicate_test@example.com",
        "tier": "developer"
    }
    
    curl_cmd = [
        "curl",
        "-X", "POST", 
        "http://127.0.0.1:8000/v1/auth/v2/register",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(test_data),
        "-s"
    ]
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            response_data = json.loads(result.stdout)
            print("Response for duplicate email:")
            print(json.dumps(response_data, indent=2))
            
            if response_data.get("status") == "error":
                print("✅ Correctly rejected duplicate email")
            else:
                print("⚠️ Duplicate email was accepted (might be first time)")
                
    except Exception as e:
        print(f"❌ Duplicate test failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Social Trends API - Simplified Registration Test")
    print("="*50)
    
    # Test principale
    success, api_key = test_api()
    
    if success:
        print("\n✅ All tests passed!")
        print("🎉 Simplified API registration is working correctly")
    else:
        print("\n❌ Tests failed")
        print("🔧 Check if server is running: source venv/bin/activate && python3 run.py")
    
    # Test email duplicata
    if success:
        test_duplicate_registration()
        
    print("\n" + "="*50)
    print("📝 Test completed")