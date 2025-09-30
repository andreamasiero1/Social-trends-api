#!/bin/bash
# Script per testare l'API dopo la configurazione DATABASE_URL

echo "🧪 Testing API after DATABASE_URL configuration..."
echo "Waiting for redeploy to complete..."
sleep 60

echo "Testing health check..."
curl -s "https://social-trends-api.onrender.com/health/detailed"
echo -e "\n"

echo "Testing registration with unique email..."
UNIQUE_EMAIL="test_$(date +%s)@example.com"
curl -X POST "https://social-trends-api.onrender.com/v1/auth/v2/register" \
-H "Content-Type: application/json" \
-d "{\"email\":\"$UNIQUE_EMAIL\",\"tier\":\"free\"}"
echo -e "\n"

echo "✅ Test completed!"