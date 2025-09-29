#!/usr/bin/env python3
"""
Script per verificare il deployment su Render dopo il fix della porta
"""
import json
import subprocess
import time
import sys

def check_deployment_status():
    """Verifica lo stato del deployment"""
    print("🚀 Verifica deployment su Render...")
    print("="*50)
    
    # URL di produzione (sostituisci con il tuo URL Render)
    production_url = "https://social-trends-api.onrender.com"
    health_endpoint = f"{production_url}/health"
    register_endpoint = f"{production_url}/v1/auth/v2/register"
    
    print(f"🌐 Testing production URL: {production_url}")
    print()
    
    # Test 1: Health Check
    print("1️⃣ Health Check...")
    try:
        result = subprocess.run([
            "curl", "-s", "-f", health_endpoint
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Health check passed")
            print(f"Response: {result.stdout}")
        else:
            print("❌ Health check failed")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
    
    print()
    
    # Test 2: API Registration
    print("2️⃣ Testing API Registration...")
    test_data = {
        "email": f"render_test_{int(time.time())}@example.com",
        "tier": "free"
    }
    
    try:
        result = subprocess.run([
            "curl", "-s", "-X", "POST", register_endpoint,
            "-H", "Content-Type: application/json",
            "-d", json.dumps(test_data)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                if response.get("status") == "success":
                    print("✅ Registration test passed")
                    print(f"API Key generated: {response.get('api_key', 'N/A')[:10]}...")
                else:
                    print("⚠️ Registration returned error:")
                    print(json.dumps(response, indent=2))
            except json.JSONDecodeError:
                print("❌ Invalid JSON response:")
                print(result.stdout)
        else:
            print("❌ Registration test failed")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Registration test error: {str(e)}")
    
    print()
    
    # Test 3: Documentation
    print("3️⃣ Testing API Documentation...")
    docs_url = f"{production_url}/docs"
    try:
        result = subprocess.run([
            "curl", "-s", "-I", docs_url
        ], capture_output=True, text=True, timeout=20)
        
        if "200 OK" in result.stdout:
            print("✅ API Documentation accessible")
            print(f"📖 Docs URL: {docs_url}")
        else:
            print("❌ Documentation not accessible")
    except Exception as e:
        print(f"❌ Documentation test error: {str(e)}")
    
    print()
    print("="*50)
    print("🏁 Deployment verification completed")
    print()
    print("💡 Next steps:")
    print("   - Check Render dashboard for deployment status")
    print("   - Monitor logs for any errors")
    print("   - Test RapidAPI integration when ready")

def check_render_logs():
    """Mostra come controllare i log di Render"""
    print("\n📋 Per controllare i log di Render:")
    print("   1. Vai su https://dashboard.render.com")
    print("   2. Clicca sul tuo servizio 'social-trends-api'")
    print("   3. Vai alla tab 'Logs'")
    print("   4. Verifica che vedi 'Uvicorn running on http://0.0.0.0:10000'")
    print("   5. Non dovrebbero esserci più errori di porta")

if __name__ == "__main__":
    print("🔧 Social Trends API - Render Deployment Checker")
    print("   (Post-fix della configurazione PORT)")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--logs":
        check_render_logs()
    else:
        check_deployment_status()
        check_render_logs()