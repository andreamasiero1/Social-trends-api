# Guida Semplice: Passare da Dati Mock a Dati Reali con PostgreSQL (Render)

Questa guida è pensata per te che "non ci capisci niente" :) Segui i passi in ordine. Non saltare.

---

## 1. Obiettivo

Attivare il database PostgreSQL reale così che:

- Le chiavi API vengano salvate e validate dal DB
- Il conteggio utilizzi / tier funzioni davvero
- Le analisi trend possano usare dati salvati (quando li inserirai)

---

## 2. Cosa useremo

- Servizio PostgreSQL su Render (o altro provider)
- File già presenti nel progetto:
  - `scripts/init_db_no_timescale.sql` (crea le tabelle base)
  - `scripts/upgrade_user_system.sql` (aggiunge utenti / email / funzione nuova)
- Variabile `DATABASE_URL` per collegare l'app

---

## 3. Prerequisiti (verifica ora)

1. Hai un database PostgreSQL creato su Render? Se no: crealo (Starter Free va bene).
2. Prendi questi dati dalla dashboard del DB Render:
   - Host
   - Porta (di solito 5432)
   - Nome database
   - Username
   - Password
3. Installa psql sul tuo Mac (se non c'è):

```bash
brew install postgresql@16
```

Verifica:

```bash
psql --version
```

Deve stampare una versione, es: `psql (PostgreSQL) 16.x`.

---

## 4. Costruisci la stringa DATABASE_URL

Formato richiesto (IMPORTANTE aggiungere `?sslmode=require` alla fine):

```
postgresql+asyncpg://social_trends_user:Mrc3NbHY6XsRUsFt6qaQOefnVcPGLPYE@Hdpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com:5432/social_trends?sslmode=require
```

Esempio:

```
postgresql+asyncpg://user_xyz:Abc12345@dpg-coolhost123.eu-central-1.postgres.render.com:5432/socialdb?sslmode=require
```

Salvala nel file `.env` (se non esiste, crealo nella root del progetto):

```

DATABASE_URL=postgresql+asyncpg://social_trends_user:Mrc3NbHY6XsRUsFt6qaQOefnVcPGLPYE@dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com:5432/ssocial_trends_vmp7?sslmode=require
ACCEPT_TEST_KEYS=true
```

(NOTA: Metti `false` solo quando tutto funziona, prima lascialo `true` se vuoi continuare a usare chiavi test finché non hai finito.)

---

## 5. Test iniziale connessione (solo client psql)

Prima prova SENZA il `+asyncpg` (psql non lo capisce). Usa:

```bash
psql "postgresql://social_trends_user:Mrc3NbHY6XsRUsFt6qaQOefnVcPGLPYE@dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com:5432/social_trends_vmp7?sslmode=require"
```


Se ottieni ancora `SSL connection has been closed unexpectedly` prova questi tentativi nell'ordine:

```bash
psql "postgres://social_trends_user:Mrc3NbHY6XsRUsFt6qaQOefnVcPGLPYE@dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com:5432/social_trends?sslmode=require&gssencmode=disable"
psql --set=sslmode=require --host=dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com --port=5432 --username=social_trends_user --dbname=social_trends
```

Se ti chiede password, inseriscila. Se entri e vedi `NOME_DB=>` sei dentro.

Se NON riesci:

- Controlla password (ricopiala lentamente)
- Rigenera password da Render e riprova
- Aggiorna psql: `brew upgrade postgresql@16`

---

## 6. Inizializza lo schema (PRIMA VOLTA)

Una volta dentro psql esci pure (\q) e dai i comandi da terminale nella cartella del progetto.

Esegui lo script base:

```bash
psql "postgres://USERNAME:PASSWORD@HOST:5432/NOME_DB?sslmode=require" -f scripts/init_db_no_timescale.sql
```

Controlla che finisca senza errori (se vedi molte righe CREATE TABLE va bene).

---

## 7. Applica l'upgrade (utente + email + nuova funzione)

```bash
psql "postgres://USERNAME:PASSWORD@HOST:5432/NOME_DB?sslmode=require" -f scripts/upgrade_user_system.sql
```

Se appare `CREATE FUNCTION` e `ALTER TABLE` tutto ok.

---

## 8. Verifica che tutto sia stato creato

Entra in psql di nuovo e digita:

```sql
\dt
```

Dovresti vedere almeno: `users`, `api_keys`, `api_usage`, `email_verifications`, `trends`, `mentions`, `hashtag_relations`.

Verifica la funzione nuova:

```sql
\df+ generate_api_key_v2
```

Se compare, bene.

Test funzione (crea una chiave finta):

```sql
-- La funzione restituisce JSON: estrai il campo api_key con ->>
SELECT (generate_api_key_v2('prova@example.com','free'))->>'api_key' AS api_key;
```

Dovresti vedere una stringa lunga tipo `sk_...`

---

## 9. Avvia l'app collegata al DB

Installa dipendenze (se non già fatto):

```bash
pip install -r requirements.txt
```

Avvia:

```bash
python run.py
```

(O qualunque comando usi di solito.)

Se parte senza errori su database -> bene.

---

## 10. Crea un utente e una chiave REALI (versione v2)

Flusso consigliato (tramite curl o Postman/RapidAPI):

1. REGISTRAZIONE:

```bash
curl -X POST http://localhost:8000/v1/auth/v2/register -H "Content-Type: application/json" -d '{"email":"nurlana14@ads24h.top","tier":"free"}'
```

Risposta attesa: JSON con `status` o messaggio verifica email (se email attiva).

2. (Facoltativo) Simula verifica email se non hai SMTP:
   In psql:

```sql
-- (Nome colonna corretto: token)
SELECT token FROM email_verifications ORDER BY created_at DESC LIMIT 1;
```

Poi:

```bash
curl "http://localhost:8000/v1/auth/v2/verify-email?token=IL_TOKEN"
```

3. GENERA CHIAVE (se previsto endpoint separato) oppure la chiave potrebbe arrivare nella risposta funzione: verifica docs della tua implementazione. In alternativa puoi usare ancora la funzione SQL manualmente e poi inserirla in `api_keys` se necessario.

4. Test con chiave:

```bash
curl -H "X-API-Key: LA_TUA_CHIAVE" http://localhost:8000/v1/trends/global
```

Se ricevi dati senza errore 401/403 la chiave è valida.

---

## 11. Popolare dati reali (Facoltativo per analisi serie)

Inserisci un trend reale di esempio:

```sql
INSERT INTO trends(keyword, platform, country, score) VALUES ('ai', 'tiktok', 'US', 87);
INSERT INTO mentions(keyword, platform, mention_count) VALUES ('ai','tiktok',1500);
INSERT INTO hashtag_relations(keyword, related_hashtag, weight) VALUES ('ai','#artificialintelligence',0.82);
```

Verifica da API (esempio):

```bash
curl -H "X-API-Key: LA_TUA_CHIAVE" "http://localhost:8000/v1/trends/keyword/ai"
```

---

## 12. Disattivare modalità test

Quando il DB funziona e hai creato chiavi reali:

1. Metti in `.env`:

```
ACCEPT_TEST_KEYS=false
```

2. Riavvia l'app
3. Le chiavi fittizie non funzioneranno più. Solo quelle nel DB.

---

## 13. Troubleshooting Rapido

| Problema                                                 | Causa comune                              | Soluzione                                                              |
| -------------------------------------------------------- | ----------------------------------------- | ---------------------------------------------------------------------- |
| `SSL connection has been closed unexpectedly`            | Versione psql / rete / parametro mancante | Aggiungi `?sslmode=require`, prova `gssencmode=disable`, aggiorna psql |
| `password authentication failed`                         | Password errata                           | Reimposta password su Render e aggiorna URL                            |
| `relation "api_keys" does not exist`                     | Script non eseguito                       | Riesegui init e upgrade (ordine corretto)                              |
| `function generate_api_key_v2 does not exist`            | Upgrade non eseguito                      | Lancia `upgrade_user_system.sql`                                       |
| API risponde con fallback / chiavi test accettate        | ACCEPT_TEST_KEYS ancora true              | Metti false e riavvia                                                  |
| 500 all'avvio app                                        | DATABASE_URL errata                       | Controlla sintassi, host, porta, `?sslmode=require`                    |
| `FATAL: no pg_hba.conf entry`                            | Host non permesso (raro su Render)        | Rigenera DB o apri ticket su Render                                    |
| `could not translate host name`                          | Host scritto male                         | Copia/incolla host esatto da Render                                    |
| Timeout di connessione                                   | Rete locale o firewall                    | Prova hotspot telefono / VPN off                                       |
| `sslmode value "require&gssencmode=disable" invalid`     | Hai concatenato male parametri            | Usa `?sslmode=require&gssencmode=disable` (una sola `?`)               |
| `psql: error: connection to server at ... refused`       | DB spento / maintenance                   | Controlla status su Render                                             |
| `could not connect to server: No such file or directory` | Server non in esecuzione                  | Avvia il server PostgreSQL                                             |
| `database "NOME_DB" does not exist`                      | Nome database errato                      | Controlla e correggi il nome del database                              |
| `user "USERNAME" does not exist`                         | Username errato                           | Controlla e correggi lo username                                       |
| `password authentication failed for user "USERNAME"`     | Password errata per l'utente              | Ricontrolla la password e riprova                                      |
| `relation "nome_tabella" does not exist`                 | Tabella non creata o nome errato          | Controlla che lo script di init sia stato eseguito correttamente       |
| `function nome_funzione does not exist`                  | Funzione non creata o nome errato         | Controlla che lo script di upgrade sia stato eseguito correttamente    |

Se ancora bloccato: raccogli comando usato + errore completo e inviamelo.

---

## 14. Checklist Finale

[ ] Connessione psql riuscita
[ ] Script init eseguito senza errori
[ ] Script upgrade eseguito
[ ] Funzione `generate_api_key_v2` visibile
[ ] Chiave reale generata e funzionante sugli endpoint
[ ] ACCEPT_TEST_KEYS impostato a false
[ ] Dati reali inseriti (facoltativo)

Quando tutti i checkbox sono veri, hai completato la migrazione dai mock al DB reale.

---

## 15. Cosa fare dopo (idee)

- Aggiungere job periodico che aggiorna tabelle trends
- Implementare rate limiting reale (incremento su `api_usage`)
- Dashboard di monitoraggio (Grafana / Metabase)

Se ti blocchi ancora sulla connessione, dammi: messaggio esatto + comando usato + versione psql.

Buon lavoro! 🚀

---

## 16. Appendice Diagnostica Avanzata (Errore: SSL connection has been closed unexpectedly)

Se dopo tutti i tentativi continui a vedere quell'errore, segui questi passi IN ORDINE. Fermati appena trovi il punto che fallisce e riportami output e numero del passo.

### 16.1 Verifica esatto hostname

Apri la dashboard Render del database e COPIA l'host esatto. Deve assomigliare a:

```
dpg-qualcosa-qualcosa.eu-central-1.postgres.render.com
```

Attenzione: nel tuo comando iniziale c'era `Hdpg-...` (H iniziale) — potrebbe essere un errore di copia. Usa solo quello che inizia con `dpg-`.

### 16.2 DNS resolution

```bash
dig +short dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com
```

Devi ottenere 1 o più indirizzi IPv4. Salvali.

### 16.3 Test porta grezzo (TCP)

```bash
nc -vz dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com 5432
```

Risultato atteso: `succeeded` o `open`. Se ottieni `Operation timed out` problema di rete/firewall.

### 16.4 Handshake TLS manuale

```bash
openssl s_client -starttls postgres -connect dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com:5432 -servername dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com </dev/null
```

Cerca le linee:

- `Protocol  : TLSv1.3` (o TLS1.2) -> OK
- `Verify return code: 0 (ok)` -> Certificato valido
  Se la connessione si chiude prima o vedi errori di handshake, segnalo.

### 16.5 Connessione al DB di servizio `postgres`

A volte il database specifico non esiste ancora o ha un nome diverso. Prova:

```bash
psql "postgres://social_trends_user:LA_PASSWORD@dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com:5432/postgres?sslmode=require"
```

Se funziona qui ma non con `social_trends`, allora il nome database è diverso da quello atteso (verificalo nella dashboard).

### 16.6 Aggiungi variabili ambiente temporanee

```bash
export PGHOST=dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com
export PGPORT=5432
export PGUSER=social_trends_user
export PGPASSWORD=LA_PASSWORD
export PGDATABASE=social_trends
export PGSSLMODE=require
psql -c "SELECT 1;"
```

Se fallisce allo stesso modo, non è un problema di URI ma della fase SSL.

### 16.7 Verbosità maggiore

```bash
PGPASSWORD=LA_PASSWORD psql "host=dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com port=5432 dbname=social_trends user=social_trends_user sslmode=require" -v VERBOSITY=verbose -c "SELECT 1;"
```

Riporta l'output completo (rimuovi la password prima di incollarlo qui).

### 16.8 Versione psql

```bash
psql --version
```

Se < 14 aggiorna:

```bash
brew update && brew upgrade postgresql@16
```

Poi ripeti il test.

### 16.9 Test con client alternativo (facile)

Installa TablePlus (gratuito base) oppure DBeaver. Prova a connetterti inserendo host, porta, user, password, database, SSL=Require. Se fallisce anche lì → problema lato server / rete.

### 16.10 Nuova password

Rigenera la password dalla dashboard Render, aggiorna tutti i comandi e riprova dal passo 16.5.

### 16.11 Crea nuovo database di prova

Su Render crea un secondo DB (nome diverso) e prova a connetterti. Se il nuovo funziona e il vecchio no → apri ticket Render per il primo database.

### 16.12 Test Python (usa asyncpg direttamente)

Crea un file `test_db_connect.py` con:

```python
import asyncio, asyncpg, os

URI = "postgresql://social_trends_user:LA_PASSWORD@dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com:5432/social_trends?sslmode=require"

async def main():
    try:
        conn = await asyncpg.connect(URI)
        v = await conn.fetchval("SELECT version();")
        print("CONNECTED:", v)
        await conn.close()
    except Exception as e:
        print("ERROR:", repr(e))

asyncio.run(main())
```

Esegui:

```bash
python test_db_connect.py
```

Riporta esattamente l'output.

### 16.13 Verifica IP pubblico tuo

A volte alcuni provider bloccano range specifici.

```bash
curl https://ifconfig.me
```

Salva l'indirizzo e (solo se richiesto) comunicalo a Render nel ticket.

### 16.14 Controlla stato Render

Vai nella pagina del DB: se c'è stato di maintenance / provisioning / restarting attendi e riprova.

### 16.15 Quando aprire un ticket

Invia a Render:

- Hostname esatto
- Orari (UTC) dei tentativi
- Output di openssl (prime 10 righe + verify code)
- Output errore psql
- IP pubblico (ifconfig.me)

---

### Cosa inviarmi ora

Per aiutarti subito mandami (senza password):

1. Host copiato dalla dashboard
2. Output dig (passo 16.2)
3. Output openssl (prime ~15 righe e le ultime 5)
4. Output comando passo 16.7
5. Output dello script Python (16.12)

Con questi posso dirti esattamente il punto in cui fallisce.

---

## 17. Escalation / Ticket a Render (pacchetto completo)

Se dopo TUTTI i passi della sezione 16 l'errore persiste (stessa chiusura SSL sia con `psql`, `asyncpg` e anche con `psycopg2`) prepara questo pacchetto e apri un ticket al supporto Render. Se non hai dati importanti nel DB attuale considera anche distruggere e ricreare il database (più rapido) PRIMA del ticket.

### 17.1 Verifica finale prima del ticket

1. Password ruotata (rigenerata da dashboard) e aggiornata nei test
2. Test rifatti con:

- `psql` (URI + parametri espliciti)
- Script `scripts/test_db_connect.py` (asyncpg)
- Script `scripts/test_psycopg_connect.py` (psycopg2)

3. Prova da rete alternativa (hotspot) effettuata
4. Nessun firewall locale (disattivato eventuale VPN / proxy)

### 17.2 File di test psycopg2

Hai già ora nel repo: `scripts/test_psycopg_connect.py`. Esegui così (dopo aver esportato la nuova DATABASE_URL):

```bash
python scripts/test_psycopg_connect.py
```

Output atteso in caso di problema server-side: eccezione immediata senza arrivare a `SELECT version()`. In caso di successo vedrai `[SUCCESS] Connected`.

### 17.3 Dati da includere nel ticket

```
Subject: PostgreSQL instance closes SSL connection immediately after TLS handshake

Hostname: dpg-d22g2immcj7s738h3v10-a.frankfurt-postgres.render.com
Database name: social_trends
User: social_trends_user
Region (come appare in dashboard): <compila>
Approx UTC timestamps of attempts: <YYYY-MM-DDTHH:MMZ>

Symptoms:
- All clients (psql, asyncpg, psycopg2) fail with: "SSL connection has been closed unexpectedly"
- TLS handshake succeeds (openssl verify return code 0)
- TCP port reachable (nc succeeded)
- DNS resolves to: <lista IP da dig>

What was tried:
1. Different connection URIs (postgresql:// and postgres://) with sslmode=require
2. Added gssencmode=disable
3. Rotated password
4. Tried connecting to default database 'postgres'
5. Tested from alternate network (hotspot)
6. Used both asyncpg and psycopg2 drivers

Request:
Please check backend logs / instance health. Looks like server terminates session immediately post-handshake before authentication phase. Kindly advise or recreate underlying instance.

Attachments (sanitized):
- OpenSSL first lines + verify code
- Full psql verbose output (without password)
- asyncpg script output
- psycopg2 script output
```

### 17.4 Opzione: Ricreare il database

Se NON hai bisogno di preservare dati:

1. Elimina l'istanza corrente dal pannello Render
2. Crea una nuova istanza (stesso piano / regione)
3. Reimposta variabili e riparti da sezione 3
4. Riesegui init + upgrade

Spesso è più veloce che attendere risposta se l'istanza è corrotta.

---

### 17.5 Se ANCHE una nuova istanza fallisce con la stessa chiusura SSL

Se hai creato una NUOVA istanza (hostname diverso, es: `dpg-d3bs0qj7mgec73a02d20-a...`) e:

- `psql` fallisce ancora con `SSL connection has been closed unexpectedly`
- `psql` verso `postgres` fallisce uguale
- `asyncpg` e `psycopg2` stesso esito
- Handshake TLS (openssl) ha `Verify return code: 0 (ok)`

Allora la probabilità che sia un problema locale crolla e rimangono:

1. Problema di piattaforma Render in quella regione / cluster
2. Qualche policy applicata all'account (raro)
3. Malfunzionamento rete interno lato provider

In questo caso:

1. Salta direttamente al ticket (17.3) includendo che PIÙ istanze nuove hanno stesso esito
2. Specifica host vecchio e host nuovo
3. Allegare output `openssl` di ENTRAMBI gli host (se diverso) e dig
4. Indicare che nessun messaggio di autenticazione viene mai ricevuto (chiusura precoce)

Opzione di mitigazione temporanea: prova a creare l'istanza in un'altra regione, se disponibile, solo per sbloccare lo sviluppo (poi migri i dati quando ripristinano la regione originale).

---
