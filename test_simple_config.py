#!/usr/bin/env python3
"""
Test semplice configurazione
"""
import os
import sys
sys.path.append('/Users/andreamasiero/Documents/Social-trends-api')

# Test caricamento .env
print("🔍 TESTING CONFIGURATION")
print("=" * 40)

# Test variabili d'ambiente
database_url = os.getenv("DATABASE_URL")
postgres_user = os.getenv("POSTGRES_USER")

print(f"DATABASE_URL: {database_url}")
print(f"POSTGRES_USER: {postgres_user}")
print()

# Test configurazione app
try:
    from api.core.config import settings
    print("✅ Settings caricati correttamente")
    print(f"DATABASE_URL from settings: {settings.get_database_url()}")
    print(f"ACCEPT_TEST_KEYS: {settings.ACCEPT_TEST_KEYS}")
except Exception as e:
    print(f"❌ Errore caricamento settings: {e}")

print("\n" + "=" * 40)
if database_url and "render.com" in database_url:
    print("✅ DATABASE_URL configurato per Render")
else:
    print("❌ DATABASE_URL non configurato o non per Render")