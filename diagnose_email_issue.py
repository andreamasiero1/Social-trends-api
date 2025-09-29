#!/usr/bin/env python3
"""
Analisi semplice del problema email senza dipendenze esterne
"""
import os

def analyze_email_issue():
    """Analizza il problema di invio email"""
    
    print("🚀 Social Trends API - Analisi Problema Email")
    print("=" * 60)
    
    # Controlla se esiste un file .env
    env_file = ".env"
    env_exists = os.path.exists(env_file)
    
    print(f"File .env presente: {'✅ Sì' if env_exists else '❌ No'}")
    
    # Controlla le variabili d'ambiente
    smtp_vars = {
        'SMTP_SERVER': os.getenv('SMTP_SERVER', ''),
        'SMTP_PORT': os.getenv('SMTP_PORT', '587'),
        'SMTP_USERNAME': os.getenv('SMTP_USERNAME', ''),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD', ''),
        'SMTP_FROM_EMAIL': os.getenv('SMTP_FROM_EMAIL', ''),
    }
    
    print("\n📧 CONFIGURAZIONE EMAIL ATTUALE:")
    print("-" * 40)
    for key, value in smtp_vars.items():
        if key == 'SMTP_PASSWORD' and value:
            print(f"{key}: ***configurata***")
        else:
            print(f"{key}: '{value}' {'❌ VUOTA' if not value else '✅ OK'}")
    
    # Determina il problema
    smtp_configured = bool(smtp_vars['SMTP_SERVER'])
    
    print("\n" + "=" * 60)
    print("🔍 DIAGNOSI:")
    
    if not smtp_configured:
        print("❌ PROBLEMA IDENTIFICATO: SMTP non configurato")
        print("\nQuando registri un utente SENZA configurazione SMTP:")
        print("• La registrazione va a buon fine")
        print("• Il token viene salvato nel database")
        print("• Il link di verifica viene SOLO stampato nei LOG del server")
        print("• Nessuna email viene effettivamente inviata")
        
        print("\n📋 SOLUZIONI:")
        print("\n1. 🔧 CONFIGURAZIONE RAPIDA CON GMAIL:")
        
        gmail_env = """
# Aggiungi queste righe al file .env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=tua-email@gmail.com
SMTP_PASSWORD=tua-app-password
SMTP_FROM_EMAIL=tua-email@gmail.com
"""
        print(gmail_env)
        
        print("📘 Come ottenere App Password Gmail:")
        print("   1. Vai su https://myaccount.google.com/security")
        print("   2. Attiva autenticazione a 2 fattori")
        print("   3. Cerca 'Password per le app'")
        print("   4. Genera password per 'Social Trends API'")
        print("   5. Usa quella password (non la tua password Gmail normale)")
        
        print("\n2. 🔗 RECUPERA IL LINK DAI LOG:")
        print("   Se hai il server in esecuzione, controlla i log")
        print("   Cerca una riga come:")
        print("   '📧 EMAIL DI VERIFICA PER yreq@honesthirianinda.net:'")
        print("   '🔗 Link: https://social-trends-api.onrender.com/v1/auth/v2/verify-email?token=...'")
        
        print("\n3. 📊 QUERY DATABASE DIRETTA:")
        query = """
SELECT 
    u.email,
    ev.token,
    ev.expires_at,
    CONCAT('https://social-trends-api.onrender.com/v1/auth/v2/verify-email?token=', ev.token) as verification_url
FROM email_verifications ev
JOIN users u ON ev.user_id = u.id
WHERE u.email = 'yreq@honesthirianinda.net' 
AND ev.verified_at IS NULL 
AND ev.expires_at > NOW()
ORDER BY ev.created_at DESC
LIMIT 1;
"""
        print("   Esegui questa query nel tuo database:")
        print(query)
        
    else:
        print("✅ SMTP configurato correttamente")
        print("Il problema potrebbe essere:")
        print("• Credenziali SMTP sbagliate")
        print("• Server SMTP bloccato")
        print("• Email finita nello spam")
    
    print("\n" + "=" * 60)
    print("🎯 AZIONE IMMEDIATA PER IL TUO CASO:")
    print("\nIl tuo utente 'yreq@honesthirianinda.net' è registrato")
    print("ma il link di verifica non è arrivato via email perché")
    print("SMTP non è configurato.")
    print("\nOpzioni:")
    print("1. Recupera il link dai log del server")
    print("2. Configura SMTP e riprova la registrazione")
    print("3. Usa la query database per recuperare il token")

def create_env_template():
    """Crea un template .env per l'email"""
    
    env_content = """# Configurazione Database
DATABASE_URL=your_database_url_here

# Configurazione Email (per invio email di verifica)
# Opzione 1: Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=tua-email@gmail.com
SMTP_PASSWORD=tua-app-password-gmail
SMTP_FROM_EMAIL=tua-email@gmail.com

# Opzione 2: SendGrid (per produzione)
# SMTP_SERVER=smtp.sendgrid.net
# SMTP_PORT=587
# SMTP_USERNAME=apikey
# SMTP_PASSWORD=tua-sendgrid-api-key
# SMTP_FROM_EMAIL=noreply@tuodominio.com

# Altri settings
SECRET_KEY=super-secret-key-change-in-production
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    
    print(f"✅ Creato file .env.template")
    print("Rinominalo in .env e compila i valori corretti")

if __name__ == "__main__":
    analyze_email_issue()
    
    print("\n" + "=" * 60)
    print("🛠️ VUOI CREARE UN TEMPLATE .env?")
    
    response = input("Premi 'y' per creare .env.template: ").lower().strip()
    if response == 'y':
        create_env_template()
    
    print("\n✨ Analisi completata!")