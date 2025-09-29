#!/usr/bin/env python3
"""
Test configurazione SMTP
"""
import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_smtp_connection():
    """Testa la connessione SMTP"""
    
    # Configurazione (da inserire manualmente per il test)
    SMTP_SERVER = input("SMTP Server (default: smtp.gmail.com): ").strip() or "smtp.gmail.com"
    SMTP_PORT = int(input("SMTP Port (default: 587): ").strip() or "587")
    SMTP_USERNAME = input("Email Gmail: ").strip()
    SMTP_PASSWORD = input("App Password Gmail: ").strip()
    
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("❌ Username e password sono richiesti!")
        return False
    
    test_email = input("Email di test per ricevere email (default: stessa di sopra): ").strip() or SMTP_USERNAME
    
    print("\n🔍 TESTING SMTP CONNECTION")
    print("=" * 40)
    print(f"Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"From: {SMTP_USERNAME}")
    print(f"To: {test_email}")
    print()
    
    try:
        # Test connessione
        print("📡 Connessione al server SMTP...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        
        print("🔒 Avvio TLS...")
        server.starttls()
        
        print("🔐 Login...")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        print("✅ Connessione riuscita!")
        
        # Invio email di test
        print("📧 Invio email di test...")
        
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = test_email
        msg['Subject'] = "🚀 Test SMTP - Social Trends API"
        
        body = """
        <html>
        <body>
            <h2>✅ SMTP Funziona!</h2>
            <p>Questo è un test della configurazione SMTP per Social Trends API.</p>
            <p>Se ricevi questa email, la configurazione è corretta! 🎉</p>
            
            <hr>
            <p><small>Test inviato da: Social Trends API SMTP Test</small></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server.send_message(msg)
        server.quit()
        
        print("🎉 EMAIL INVIATA CON SUCCESSO!")
        print(f"📬 Controlla la casella email: {test_email}")
        print()
        print("🔧 Se hai ricevuto l'email, usa queste configurazioni su Render:")
        print(f"SMTP_SERVER={SMTP_SERVER}")
        print(f"SMTP_PORT={SMTP_PORT}")
        print(f"SMTP_USE_TLS=true")
        print(f"SMTP_USERNAME={SMTP_USERNAME}")
        print(f"SMTP_PASSWORD={SMTP_PASSWORD}")
        print(f"SMTP_FROM_EMAIL={SMTP_USERNAME}")
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ ERRORE AUTENTICAZIONE!")
        print("Verifica:")
        print("1. Email corretta")
        print("2. App Password corretta (NON la password normale)")
        print("3. Autenticazione a 2 fattori attivata")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ ERRORE SMTP: {e}")
        return False
        
    except Exception as e:
        print(f"❌ ERRORE GENERICO: {e}")
        return False

def show_gmail_setup_guide():
    """Mostra la guida per configurare Gmail"""
    print("\n📘 GUIDA CONFIGURAZIONE GMAIL")
    print("=" * 50)
    print("1. Vai su: https://myaccount.google.com/security")
    print("2. Attiva 'Verifica in due passaggi' se non attiva")
    print("3. Cerca 'Password per le app'")
    print("4. Clicca 'Seleziona app' → 'Altro (nome personalizzato)'")
    print("5. Scrivi 'Social Trends API'")
    print("6. Copia la password di 16 caratteri generata")
    print("7. Usa QUELLA password (non quella normale di Gmail)")
    print()
    print("📝 Formato App Password: abcd efgh ijkl mnop")
    print("⚠️  IMPORTANTE: Usa la App Password, non la password normale!")

if __name__ == "__main__":
    print("🚀 Social Trends API - SMTP Configuration Test")
    
    choice = input("\n1. Test SMTP\n2. Guida Gmail\nScegli (1-2): ").strip()
    
    if choice == "2":
        show_gmail_setup_guide()
    elif choice == "1":
        test_smtp_connection()
    else:
        print("Scelta non valida. Usa 1 o 2.")