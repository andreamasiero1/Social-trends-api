## 🚨 SOLUZIONE ALTERNATIVA - Se DATABASE_URL non funziona

### **Invece di configurare DATABASE_URL, configura queste 5 variabili separate:**

1. **Web Service** → **Environment** → **Add Variables**:

   ```
   POSTGRES_SERVER = dpg-xyz.frankfurt-postgres.render.com
   POSTGRES_PORT = 5432
   POSTGRES_USER = social_trends_user
   POSTGRES_PASSWORD = [la tua password]
   POSTGRES_DB = social_trends_vmp7
   ```

2. **Come ottenere questi valori:**

   - Vai nel **database** "social-trends"
   - **Connections** → **External Database URL**
   - Esempio URL: `postgresql://user:pass@host:port/db`
   - Dividi così:
     ```
     postgresql://social_trends_user:hM5MIzSqMlbCZrb8412qekjnnqmEVlnw@dpg-d3bs0qj7mgec73a02d20-a.frankfurt-postgres.render.com/social_trends_vmp7
     ```
     Diventa:
     ```
     POSTGRES_USER = social_trends_user
     POSTGRES_PASSWORD = hM5MIzSqMlbCZrb8412qekjnnqmEVlnw
     POSTGRES_SERVER = dpg-d3bs0qj7mgec73a02d20-a.frankfurt-postgres.render.com
     POSTGRES_PORT = 5432
     POSTGRES_DB = social_trends_vmp7
     ```

3. **Save Changes** e aspetta il redeploy

### **Test dopo la configurazione:**

```bash
curl -s "https://social-trends-api.onrender.com/health/detailed"
# Dovrebbe mostrare: "database":"connected"
```

Prova prima con DATABASE_URL, se non funziona usa questo metodo alternativo!
