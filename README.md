# Social Trends API

🚀 **Real-time Social Media Trends API** - Aggregatore di trend da TikTok e Instagram in tempo reale.

## ✨ Caratteristiche

- 📈 **Trend Globali**: Aggregazione intelligente da tutte le piattaforme
- 📱 **Trend per Piattaforma**: Dati specifici per TikTok e Instagram
- 🌍 **Filtri geografici**: Trend per paese (piano Business+)
- 🔍 **Analisi Keywords**: Sentiment e timeline (piano Developer+)
- 🔗 **Hashtag correlati**: Scopri contenuti correlati
- 🔑 **Sistema API Key**: Autenticazione e rate limiting

## 📊 Piani disponibili

| Piano          | Chiamate/mese | Funzionalità                           |
| -------------- | ------------- | -------------------------------------- |
| **Free**       | 1.000         | Trend globali                          |
| **Developer**  | 10.000        | Tutti gli endpoint base                |
| **Business**   | 50.000        | Analytics avanzate + filtri geografici |
| **Enterprise** | 200.000       | Supporto prioritario                   |

## 🚀 Endpoints

### Trend Globali

```
GET /v1/trends/global?limit=10
```

### Trend per Piattaforma

```
GET /v1/trends/platform?source=tiktok&limit=20
GET /v1/trends/platform?source=instagram&limit=20
```

### Trend per Paese

```
GET /v1/trends/country?code=IT&limit=10
```

### Analisi Keyword

```
GET /v1/trends/analysis/keyword?keyword=fashion&hours=24
```

### Hashtag Correlati

```
GET /v1/trends/hashtags/related?hashtag=fashion&limit=10
```

## 🔑 Autenticazione

Tutte le richieste richiedono un header `X-API-Key`:

```bash
curl -H "X-API-Key: your-api-key" \
  "https://social-trends-api.onrender.com/v1/trends/global"
```

### Genera API Key

```
POST /v1/auth/generate-key?email=your@email.com&tier=developer
```

## 🛠️ Tecnologie

- **FastAPI**: Framework web moderno e veloce
- **PostgreSQL + TimescaleDB**: Database ottimizzato per serie temporali
- **Redis**: Caching e queue management
- **Docker**: Containerizzazione
- **Render**: Hosting cloud

## 📚 Documentazione

Documentazione interattiva disponibile su:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## 🌟 Esempi di Utilizzo

### JavaScript/Node.js

```javascript
const response = await fetch(
  "https://social-trends-api.onrender.com/v1/trends/global?limit=5",
  {
    headers: { "X-API-Key": "your-api-key" },
  }
);
const trends = await response.json();
console.log(trends);
```

### Python

```python
import requests

response = requests.get(
    'https://social-trends-api.onrender.com/v1/trends/global?limit=5',
    headers={'X-API-Key': 'your-api-key'}
)
trends = response.json()
print(trends)
```

### cURL

```bash
curl -H "X-API-Key: your-api-key" \
  "https://social-trends-api.onrender.com/v1/trends/global?limit=5"
```

## 🔧 Sviluppo Locale

```bash
# Clone del repository
git clone https://github.com/your-username/social-trends-api.git
cd social-trends-api

# Setup ambiente virtuale
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure: venv\Scripts\activate  # Windows

# Installa dipendenze
pip install -r requirements.txt

# Avvia servizi Docker
docker-compose up -d

# Avvia API
python run.py
```

L'API sarà disponibile su http://localhost:8000

## 📈 Roadmap

- [ ] Integrazione API ufficiali TikTok/Instagram
- [ ] Analytics real-time con WebSocket
- [ ] Machine Learning per predizioni trend
- [ ] Dashboard web admin
- [ ] Webhooks per notifiche trend

## 📞 Supporto

- **Email**: support@socialtrends.api
- **Documentazione**: https://social-trends-api.onrender.com/docs
- **Status**: https://status.socialtrends.api

---

Creato con ❤️ da Andrea Masiero
