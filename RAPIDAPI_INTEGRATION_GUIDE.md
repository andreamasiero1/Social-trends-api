# 🔑 API Key Management - Alternative Senza Email

## 🚀 **Endpoint per RapidAPI Users**

### **1. Registrazione Istantanea (Raccomandato)**

**Endpoint:** `POST /v1/auth/v2/register-instant`

**Vantaggi:**

- ✅ API key immediata
- ✅ No email verification
- ✅ Perfetto per marketplace
- ✅ Un solo step

**Request:**

```json
{
  "email": "user@example.com",
  "tier": "free"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "🎉 API key generata con successo!",
  "api_key": "api_1234567890abcdef",
  "tier": "free",
  "email": "user@example.com",
  "monthly_limit": 1000,
  "note": "⚠️ Salva questa API key in un posto sicuro."
}
```

**Test:**

```bash
curl -X POST https://social-trends-api.onrender.com/v1/auth/v2/register-instant \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","tier":"free"}'
```

---

### **2. Recupero API Key Esistenti**

**Endpoint:** `GET /v1/auth/v2/keys/{email}`

**Utilità:**

- 🔍 Recupera chiavi perse
- 📊 Mostra statistiche utilizzo
- 🔑 Lista tutte le chiavi attive

**Request:**

```
GET /v1/auth/v2/keys/user@example.com
```

**Response:**

```json
{
  "status": "success",
  "email": "user@example.com",
  "total_keys": 2,
  "keys": [
    {
      "api_key": "api_1234567890abcdef",
      "tier": "free",
      "created_at": "2025-09-28T12:00:00",
      "monthly_requests": 150,
      "monthly_limit": 1000,
      "last_used": "2025-09-28T11:30:00"
    }
  ]
}
```

**Test:**

```bash
curl https://social-trends-api.onrender.com/v1/auth/v2/keys/test@example.com
```

---

## 🎯 **Flussi Raccomandati per RapidAPI**

### **Flusso A: Registrazione Rapida (1 Step)**

```
User → POST /register-instant → Get API Key → Start Using API
```

### **Flusso B: Recupero Chiave**

```
User forgot key → GET /keys/{email} → Get existing keys
```

### **Flusso C: Tradizionale (2 Steps) - Opzionale**

```
User → POST /register → Email verification → GET /verify-email → Get API Key
```

---

## 📋 **Confronto Metodi**

| Metodo              | Velocità     | Email Richiesta | Verifica | Uso RapidAPI        |
| ------------------- | ------------ | --------------- | -------- | ------------------- |
| `/register-instant` | ⚡ Immediato | ✅ Sì           | ❌ No    | ⭐⭐⭐⭐⭐ Perfetto |
| `/register`         | 🐌 2 step    | ✅ Sì           | ✅ Sì    | ⭐⭐⭐ Ok           |
| `/keys/{email}`     | ⚡ Immediato | ✅ Sì           | ❌ No    | ⭐⭐⭐⭐ Recovery   |

---

## 🔧 **Configurazione RapidAPI**

**Per marketplace API come RapidAPI, usa:**

1. **Endpoint principale:** `/register-instant`
2. **Endpoint recovery:** `/keys/{email}`
3. **Documentazione:** Mostra solo questi due endpoint
4. **UX:** Single-step registration

**Vantaggi per utenti RapidAPI:**

- ✅ Zero friction onboarding
- ✅ No email verification delays
- ✅ Immediate API access
- ✅ Self-service key recovery
