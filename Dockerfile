FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice
COPY . .

# Esponi la porta (sarà determinata dalla variabile PORT)
EXPOSE $PORT

# Comando per avviare l'app - usa la variabile PORT di Render
CMD uvicorn api.main:app --host 0.0.0.0 --port $PORT
