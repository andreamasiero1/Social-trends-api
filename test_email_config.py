#!/usr/bin/env python3
"""
Test per verificare la configurazione email
"""
import os
import asyncio
from api.core.config import settings
from api.services.email_service import EmailService

async def test_email_configuration():
    """Testa la configurazione email corrente"""
    
    print("🔍 ANALISI CONFIGURAZIONE EMAIL")
    print("=" * 50)
    
    # Controlla le variabili di configurazione
    print(f"SMTP_SERVER: '{settings.SMTP_SERVER}'")
    print(f"SMTP_PORT: {settings.SMTP_PORT}")
    print(f"SMTP_USE_TLS: {settings.SMTP_USE_TLS}")
    print(f"SMTP_USERNAME: '{settings.SMTP_USERNAME}'")
    print(f"SMTP_PASSWORD: {'***nascosta***' if settings.SMTP_PASSWORD else 'NON CONFIGURATA'}")
    print(f"SMTP_FROM_EMAIL: '{settings.SMTP_FROM_EMAIL}'")
    
    print("\n" + "=" * 50)
    
    if not settings.SMTP_SERVER:
        print("❌ PROBLEMA IDENTIFICATO:")
        print("Le variabili SMTP non sono configurate!")
        print("\n📝 SOLUZIONI POSSIBILI:")
        print("\n1. 🔧 CONFIGURAZIONE GMAIL (più semplice):")
        print("   - Crea un file .env nella root del progetto")
        print("   - Aggiungi queste righe:")
        print("     SMTP_SERVER=smtp.gmail.com")
        print("     SMTP_PORT=587")
        print("     SMTP_USE_TLS=true")
        print("     SMTP_USERNAME=tua-email@gmail.com")
        print("     SMTP_PASSWORD=tua-app-password-gmail")
        print("     SMTP_FROM_EMAIL=tua-email@gmail.com")
        print("\n   📘 Come ottenere App Password Gmail:")
        print("     1. Vai su https://myaccount.google.com/security")
        print("     2. Attiva l'autenticazione a 2 fattori")
        print("     3. Cerca 'Password per le app'")
        print("     4. Genera password per 'Social Trends API'")
        print("     5. Usa quella password nel campo SMTP_PASSWORD")
        
        print("\n2. 🌐 CONFIGURAZIONE SENDGRID (per produzione):")
        print("   - Registrati su https://sendgrid.com")
        print("   - Ottieni API key")
        print("   - Configura:")
        print("     SMTP_SERVER=smtp.sendgrid.net")
        print("     SMTP_PORT=587")
        print("     SMTP_USERNAME=apikey")
        print("     SMTP_PASSWORD=tua-sendgrid-api-key")
        
        print("\n3. 🔗 MODALITÀ SVILUPPO (link diretto):")
        print("   Il link di verifica è stato comunque generato!")
        print("   Controlla i log del server dove viene stampato il link diretto.")
        print("   Il link avrà questa forma:")
        print("   https://social-trends-api.onrender.com/v1/auth/v2/verify-email?token=...")
        
    else:
        print("✅ CONFIGURAZIONE SMTP PRESENTE")
        print("Testando connessione SMTP...")
        
        try:
            import smtplib
            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.quit()
            print("✅ Connessione SMTP riuscita!")
        except Exception as e:
            print(f"❌ Errore connessione SMTP: {e}")
            print("Controlla username, password e impostazioni del server.")

def show_email_verification_link():
    """Mostra come recuperare il link di verifica dai log"""
    print("\n" + "=" * 50)
    print("🔗 RECUPERARE IL LINK DI VERIFICA")
    print("=" * 50)
    print("Se hai appena registrato un utente e l'email non è configurata,")
    print("il link di verifica è stato stampato nei log del server.")
    print("\nCerca nel terminale dove hai avviato il server (python run.py)")
    print("un messaggio simile a:")
    print("📧 EMAIL DI VERIFICA PER yreq@honesthirianinda.net:")
    print("🔗 Link: https://social-trends-api.onrender.com/v1/auth/v2/verify-email?token=...")
    print("\nOppure controlla il database per recuperare il token:")

async def get_verification_token_from_db(email: str):
    """Recupera il token di verifica dal database per un email"""
    try:
        from api.core.database import execute_query
        
        result = await execute_query(
            """
            SELECT ev.token, ev.expires_at, u.email
            FROM email_verifications ev
            JOIN users u ON ev.user_id = u.id
            WHERE u.email = $1 
            AND ev.verified_at IS NULL 
            AND ev.expires_at > NOW()
            ORDER BY ev.created_at DESC
            LIMIT 1
            """,
            email,
            fetch="one"
        )
        
        if result:
            token = result['token']
            expires_at = result['expires_at']
            verification_url = f"https://social-trends-api.onrender.com/v1/auth/v2/verify-email?token={token}"
            
            print(f"\n✅ TOKEN TROVATO PER {email}:")
            print(f"🔗 Link di verifica: {verification_url}")
            print(f"⏰ Scade il: {expires_at}")
            return verification_url
        else:
            print(f"\n❌ Nessun token attivo trovato per {email}")
            return None
            
    except Exception as e:
        print(f"❌ Errore nel recupero del token: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Social Trends API - Test Configurazione Email\n")
    
    # Testa la configurazione
    asyncio.run(test_email_configuration())
    
    # Mostra come recuperare il link
    show_email_verification_link()
    
    # Se specifichi un email, cerca il token nel database
    import sys
    if len(sys.argv) > 1:
        email = sys.argv[1]
        print(f"\n🔍 Cercando token per {email}...")
        asyncio.run(get_verification_token_from_db(email))
    
    print("\n" + "=" * 50)
    print("💡 Per risolvere il problema:")
    print("1. Configura SMTP nel file .env")
    print("2. Oppure recupera il link dai log del server")
    print("3. Oppure usa questo script: python test_email_config.py email@example.com")