# 🚀 GUIDA DEPLOYMENT SOCIAL TRENDS API

## 📊 STATO ATTUALE

✅ **Completato:**

- Sistema utenti migliorato implementato
- Email verification system completo
- Integrazione RapidAPI per provisioning API keys
- Test suite completa (96.2% successo)
- Codice pushato su GitHub (commit bdbb876)

⏳ **In corso:**

- Deployment automatico su Render (triggering da git push)
- Applicazione nuove modifiche alla produzione

---

## 🔍 VERIFICA DEPLOYMENT

### 1. Monitoraggio Automatico

```bash
# Controlla stato deployment ogni 5 minuti
/Users/andreamasiero/Documents/Social-trends-api/.venv/bin/python monitor_deployment.py
```

### 2. Verifica Manuale

- **URL API:** https://social-trends-api.onrender.com
- **Documentazione:** https://social-trends-api.onrender.com/docs
- **Dashboard Render:** https://dashboard.render.com

### 3. Indicatori di Successo

- ✅ Endpoint `/api/v2/auth/register` disponibile
- ✅ Endpoint `/api/v2/auth/my-account` disponibile
- ✅ Endpoint `/api/v2/auth/rapidapi/provision` disponibile
- ✅ Documentazione OpenAPI aggiornata

---

## 🗄️ AGGIORNAMENTO DATABASE

### 1. Preparazione

```bash
# Test connessione database produzione
export DATABASE_URL="postgresql://username:password@host:port/database"
/Users/andreamasiero/Documents/Social-trends-api/.venv/bin/python check_render_deploy.py
```

### 2. Esecuzione Upgrade

```bash
# Applica modifiche schema database
/Users/andreamasiero/Documents/Social-trends-api/.venv/bin/python scripts/upgrade_database.py
```

### 3. Verifiche Post-Upgrade

- ✅ Tabella `users` creata
- ✅ Tabella `email_verifications` creata
- ✅ Funzione `get_user_from_api_key_with_fallback` aggiornata
- ✅ 9 utenti esistenti migrati correttamente

---

## 🧪 TEST PRODUZIONE

### 1. Test Autenticazione

```bash
# Test registrazione nuovo utente
curl -X POST "https://social-trends-api.onrender.com/api/v2/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "confirmPassword": "SecurePass123!"
  }'
```

### 2. Test Email Verification

```bash
# Test verifica email (con token ricevuto via email)
curl -X POST "https://social-trends-api.onrender.com/api/v2/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d '{"token": "verification_token_here"}'
```

### 3. Test RapidAPI Provisioning

```bash
# Test provisioning API key
curl -X POST "https://social-trends-api.onrender.com/api/v2/auth/rapidapi/provision" \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Proxy-Secret: your_secret" \
  -d '{
    "email": "verified@user.com",
    "rapidapi_user_id": "12345",
    "subscription_type": "premium"
  }'
```

---

## 📧 CONFIGURAZIONE EMAIL

### Variabili d'Ambiente Richieste

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@socialtrends.api
EMAIL_FROM_NAME=Social Trends API
```

### Test Email Service

```bash
# Test invio email verificazione
/Users/andreamasiero/Documents/Social-trends-api/.venv/bin/python -c "
import asyncio
from api.services.email_service import send_verification_email
asyncio.run(send_verification_email('test@example.com', 'test_token'))
"
```

---

## 👥 MIGRAZIONE UTENTI ESISTENTI

### Strategia Zero-Downtime

1. **Backward Compatibility**: Sistema mantiene compatibilità con API keys esistenti
2. **Migrazione Graduale**: Utenti esistenti continueranno a funzionare
3. **Invito Upgrade**: Email informativa sui nuovi features

### Script Notifica Utenti

```sql
-- Recupera email utenti esistenti per notifica
SELECT DISTINCT user_email, tier, COUNT(*) as api_keys
FROM api_keys
WHERE user_email IS NOT NULL
GROUP BY user_email, tier
ORDER BY tier, user_email;
```

---

## 📚 AGGIORNAMENTO DOCUMENTAZIONE

### 1. OpenAPI Schema

- ✅ Nuovi endpoint auth v2 documentati
- ✅ Modelli Pydantic aggiornati
- ✅ Esempi di richiesta/risposta

### 2. README.md

- ✅ Sezione registrazione utenti
- ✅ Processo verifica email
- ✅ Integrazione RapidAPI

### 3. RapidAPI Marketplace

- 📝 Aggiornare descrizione API
- 📝 Aggiungere esempi nuovi endpoint
- 📝 Pubblicare pricing plans aggiornati

---

## ⚠️ TROUBLESHOOTING

### Problemi Comuni

**1. Endpoint 404**

- Verifica deployment completato su Render
- Controlla logs deployment per errori
- Verifica che git push sia arrivato correttamente

**2. Database Connection Error**

- Verifica DATABASE_URL configurato correttamente
- Controlla che database sia attivo su Render
- Testa connessione con check_render_deploy.py

**3. Email Non Inviate**

- Verifica configurazione SMTP su Render
- Controlla variabili d'ambiente email
- Testa con account Gmail App Password

**4. API Keys Non Funzionanti**

- Verifica migrazione database completata
- Controlla funzione fallback attiva
- Testa con chiavi esistenti prima dell'upgrade

---

## 📞 CONTATTI E SUPPORTO

**Render Dashboard:** https://dashboard.render.com
**GitHub Repository:** https://github.com/your-username/social-trends-api
**Email Support:** your-email@domain.com

---

## 🎯 CHECKLIST FINALE

### Pre-Deploy

- [x] Codice testato localmente (96.2% successo)
- [x] Tutti i test unit passano
- [x] Compatibilità backward verificata
- [x] Commit pushato su GitHub

### Deploy

- [ ] Render deployment completato
- [ ] Nuovi endpoint disponibili
- [ ] Documentazione aggiornata online

### Post-Deploy

- [ ] Database upgrade eseguito
- [ ] Test produzione completati
- [ ] Email service configurato
- [ ] Utenti esistenti notificati
- [ ] Monitoring attivo

---

_📅 Ultimo aggiornamento: 2025-08-18 11:10_
_🔧 Versione: 2.0.0 (Sistema Utenti Migliorato)_
