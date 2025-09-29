#!/usr/bin/env python3
"""
Raccoglie diagnostica completa sulla connessione PostgreSQL:
- Variabili ambiente principali
- dig, nc, openssl (TLS handshake)
- psql verso DB target e verso 'postgres'
- Test asyncpg
- Test psycopg2
Output salvato in file: db_diagnostics_<timestamp>.log

USO:
  1. Esporta prima le variabili (o almeno DATABASE_URL) es: 
     export DATABASE_URL="postgresql://user:PASS@host:5432/dbname?sslmode=require"
  2. (Opzionale) export PGHOST / PGUSER / PGPASSWORD ...
  3. python scripts/collect_db_diagnostics.py
  4. Rivedi il file generato e RIMUOVI password prima di condividerlo.
"""
import os, sys, shlex, subprocess, datetime, re, textwrap
from pathlib import Path

TIMESTAMP = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
OUT_FILE = Path(f'db_diagnostics_{TIMESTAMP}.log')

DB_URL = os.getenv('DATABASE_URL','')

# Sanitizzazione password nell'URL
PASSWORD_MASK = '***REDACTED***'
SANITIZED_URL = DB_URL
if DB_URL:
    SANITIZED_URL = re.sub(r'(postgres(?:ql)?://[^:]+:)([^@]+)(@)', rf'\1{PASSWORD_MASK}\3', DB_URL)

HOST = os.getenv('PGHOST') or re.search(r'@([^:/?]+)', DB_URL or '')
if HOST:
    HOST = HOST if isinstance(HOST, str) else HOST.group(1)
PORT = os.getenv('PGPORT','5432')
USER = os.getenv('PGUSER') or (re.search(r'//([^:]+):', DB_URL or '') or [None, ''])[1]
DBNAME = os.getenv('PGDATABASE') or (re.search(r'/([^/?]+)', DB_URL.split('@')[-1] if '@' in DB_URL else '') or [None,''])[1]

# Comandi base
commands = []

def add_cmd(name, cmd, env=None):
    commands.append({"name": name, "cmd": cmd, "env": env or {}})

if HOST:
    add_cmd('dig', f'dig +short {HOST}')
    add_cmd('nc', f'nc -vz {HOST} {PORT}')
    add_cmd('openssl', f'openssl s_client -starttls postgres -connect {HOST}:{PORT} -servername {HOST} </dev/null')

# psql target DB
if HOST and USER and DBNAME:
    psql_conn_parts = f'host={HOST} port={PORT} dbname={DBNAME} user={USER} sslmode=require'
    add_cmd('psql_select1_target', f'psql "{psql_conn_parts}" -c "SELECT 1;"')
    # psql default db 'postgres'
    add_cmd('psql_select1_postgres', f'psql "host={HOST} port={PORT} dbname=postgres user={USER} sslmode=require" -c "SELECT 1;"')

# asyncpg test snippet
ASYNC_PY = f"""import asyncio, asyncpg, os, sys\nuri=os.getenv('DATABASE_URL')\nif uri and '+asyncpg' in uri: uri=uri.replace('+asyncpg','')\nasync def main():\n  try:\n    conn= await asyncpg.connect(uri)\n    v= await conn.fetchval('SELECT version();')\n    print('ASYNC_SUCCESS', v)\n    await conn.close()\n  except Exception as e:\n    print('ASYNC_ERROR', type(e).__name__, repr(e))\nasyncio.run(main())\n"""
add_cmd('python_asyncpg', f'python - <<"PY"\n{ASYNC_PY}PY')

# psycopg2 test
PSY_PY = f"""import psycopg2, os, re\nurl=os.getenv('DATABASE_URL')\nif url and '+asyncpg' in url: url=url.replace('+asyncpg','')\ntry:\n  conn=psycopg2.connect(url, connect_timeout=8)\n  cur=conn.cursor();cur.execute('SELECT version();');print('PSYCOPG2_SUCCESS',cur.fetchone()[0]);cur.close();conn.close()\nexcept Exception as e:\n  print('PSYCOPG2_ERROR', type(e).__name__, e)\n"""
add_cmd('python_psycopg2', f'python - <<"PY"\n{PSY_PY}PY')

HEADER = f"""==== DB DIAGNOSTICS ({TIMESTAMP} UTC) ====
Environment summary (password redatta):
  DATABASE_URL = {SANITIZED_URL or 'NON DEFINITA'}
  PGHOST={HOST} PGPORT={PORT} PGUSER={USER} PGDATABASE={DBNAME}
Python: {sys.version.split()[0]}
Working dir: {os.getcwd()}
===========================================\n"""

with OUT_FILE.open('w', encoding='utf-8') as f:
    f.write(HEADER)
    for item in commands:
        f.write(f"\n----- CMD: {item['name']} -----\n$ {item['cmd']}\n")
        try:
            proc = subprocess.run(item['cmd'], shell=True, capture_output=True, text=True, timeout=25, env={**os.environ, **item['env']})
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()
            if stdout:
                f.write('[STDOUT]\n' + stdout + '\n')
            if stderr:
                f.write('[STDERR]\n' + stderr + '\n')
            f.write(f'[RETURN_CODE] {proc.returncode}\n')
        except subprocess.TimeoutExpired:
            f.write('[ERROR] TIMEOUT\n')
        except Exception as e:
            f.write(f'[EXCEPTION] {e}\n')

print(f"File diagnostica generato: {OUT_FILE}")
print("Apri il file, rimuovi eventuali password residue (cerca la stringa) e poi condividilo (o incolla le parti rilevanti).")
