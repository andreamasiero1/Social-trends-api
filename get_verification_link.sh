#!/bin/bash

# Script per recuperare il link di verifica dal database PostgreSQL

EMAIL="yreq@honesthirianinda.net"

echo "🔍 Recuperando link di verifica per: $EMAIL"
echo "================================================================"

# Query per recuperare il token
QUERY="SELECT 
    u.email,
    ev.token,
    ev.expires_at,
    CONCAT('https://social-trends-api.onrender.com/v1/auth/v2/verify-email?token=', ev.token) as verification_url
FROM email_verifications ev
JOIN users u ON ev.user_id = u.id
WHERE u.email = '$EMAIL' 
AND ev.verified_at IS NULL 
AND ev.expires_at > NOW()
ORDER BY ev.created_at DESC
LIMIT 1;"

echo "Tentativo di connessione al database locale..."

# Prova diverse modalità di connessione
if command -v psql >/dev/null 2>&1; then
    echo "✅ psql disponibile, connessione in corso..."
    
    # Prova con parametri dall'environment
    export PGPASSWORD="postgres123"
    result=$(psql -h localhost -p 5432 -U postgres -d social_trends -c "$QUERY" -t -A 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$result" ]; then
        echo "✅ TOKEN TROVATO!"
        echo "================================================================"
        echo "$result" | while IFS='|' read email token expires_at url; do
            echo "📧 Email: $email"
            echo "⏰ Scade: $expires_at"
            echo "🔗 Link di verifica:"
            echo "   $url"
        done
        echo "================================================================"
        echo ""
        echo "💡 Copia e incolla il link nel browser per verificare l'email"
    else
        echo "❌ Nessun token attivo trovato o errore di connessione"
        echo ""
        echo "POSSIBILI CAUSE:"
        echo "• Database non in esecuzione"
        echo "• Token già utilizzato o scaduto"  
        echo "• Email non registrata"
        echo "• Credenziali database sbagliate"
        echo ""
        echo "🔧 QUERY MANUALE:"
        echo "Se hai accesso diretto al database, esegui:"
        echo "$QUERY"
    fi
else
    echo "❌ psql non disponibile"
    echo ""
    echo "SOLUZIONI ALTERNATIVE:"
    echo ""
    echo "1. 📊 QUERY MANUALE NEL TUO CLIENT DATABASE:"
    echo "$QUERY"
    echo ""
    echo "2. 🔧 CONFIGURA SMTP E REGISTRA DI NUOVO:"
    echo "   - Modifica il file .env aggiungendo:"
    echo "     SMTP_SERVER=smtp.gmail.com"
    echo "     SMTP_PORT=587" 
    echo "     SMTP_USE_TLS=true"
    echo "     SMTP_USERNAME=tua-email@gmail.com"
    echo "     SMTP_PASSWORD=tua-app-password"
    echo "     SMTP_FROM_EMAIL=tua-email@gmail.com"
    echo ""
    echo "3. 🔍 CERCA NEI LOG DEL SERVER:"
    echo "   Il link è stato stampato nei log quando hai fatto la registrazione"
    echo "   Cerca: '📧 EMAIL DI VERIFICA PER $EMAIL:'"
fi

echo ""
echo "================================================================"
echo "🎯 RIEPILOGO PROBLEMA:"
echo "L'API ha registrato l'utente correttamente ma non ha inviato"
echo "l'email perché SMTP non è configurato nel file .env"
echo ""
echo "La registrazione è andata a buon fine, serve solo recuperare"
echo "il link di verifica dal database o dai log del server."