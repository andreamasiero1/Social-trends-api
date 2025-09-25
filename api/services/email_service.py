import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from api.core.config import settings
from api.core.database import execute_query
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Servizio per gestire l'invio di email di verifica."""
    
    @staticmethod
    async def send_verification_email(email: str, user_id: int) -> str:
        """Invia email di verifica e restituisce il token generato."""
        
        # Genera token di verifica
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # Salva token nel database
        await execute_query(
            """
            INSERT INTO email_verifications (user_id, token, expires_at)
            VALUES ($1, $2, $3)
            """,
            user_id, verification_token, expires_at
        )
        
        # URL di verifica (in produzione useresti il tuo dominio)
        verification_url = f"https://social-trends-api.onrender.com/v1/auth/v2/verify-email?token={verification_token}"
        
        # Contenuto dell'email
        email_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">🚀 Social Trends API</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <h2 style="color: #333; margin-bottom: 20px;">Verifica la tua Email</h2>
                
                <p style="color: #666; line-height: 1.6; margin-bottom: 25px;">
                    Grazie per esserti registrato alla Social Trends API! 
                    Per completare la registrazione e ricevere la tua API key, 
                    clicca sul pulsante qui sotto:
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background: #667eea; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 5px; font-weight: bold;
                              display: inline-block;">
                        ✅ Verifica Email
                    </a>
                </div>
                
                <p style="color: #999; font-size: 14px; margin-top: 30px;">
                    Se non riesci a cliccare il pulsante, copia e incolla questo link nel tuo browser:<br>
                    <code style="background: #f1f1f1; padding: 5px; border-radius: 3px; word-break: break-all;">
                        {verification_url}
                    </code>
                </p>
                
                <p style="color: #999; font-size: 12px; margin-top: 20px;">
                    Questo link scadrà tra 24 ore. Se non hai richiesto questa registrazione, ignora questa email.
                </p>
            </div>
            
            <div style="background: #333; color: #999; padding: 20px; text-align: center; font-size: 12px;">
                Social Trends API - Trend Aggregation Service<br>
                Questo è un messaggio automatico, non rispondere a questa email.
            </div>
        </body>
        </html>
        """
        
        try:
            # Se hai configurato SMTP (Gmail, SendGrid, etc.)
            if settings.SMTP_SERVER:
                await EmailService._send_smtp_email(
                    to_email=email,
                    subject="🚀 Verifica la tua email - Social Trends API",
                    html_content=email_content
                )
            else:
                # Per ora, logga il contenuto (in sviluppo)
                logger.info(f"Email di verifica per {email}: {verification_url}")
                print(f"\n📧 EMAIL DI VERIFICA PER {email}:")
                print(f"🔗 Link: {verification_url}")
                print("-" * 50)
        
        except Exception as e:
            logger.error(f"Errore nell'invio email a {email}: {str(e)}")
            # Non bloccare la registrazione anche se l'email fallisce
        
        return verification_token
    
    @staticmethod
    async def _send_smtp_email(to_email: str, subject: str, html_content: str):
        """Invia email tramite SMTP (da configurare con il tuo provider)."""
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
    
    @staticmethod
    async def verify_email_token(token: str) -> dict:
        """Verifica un token di email e attiva l'utente."""
        
        # Cerca il token nel database
        verification = await execute_query(
            """
            SELECT ev.*, u.email, u.id as user_id
            FROM email_verifications ev
            JOIN users u ON ev.user_id = u.id
            WHERE ev.token = $1 
            AND ev.verified_at IS NULL 
            AND ev.expires_at > NOW()
            """,
            token,
            fetch="one"
        )
        
        if not verification:
            return {
                "success": False,
                "message": "Token non valido o scaduto."
            }
        
        # Marca l'email come verificata
        await execute_query(
            "UPDATE email_verifications SET verified_at = NOW() WHERE token = $1",
            token
        )
        
        await execute_query(
            "UPDATE users SET is_email_verified = TRUE WHERE id = $1",
            verification['user_id']
        )
        
        # Genera l'API key finale
        result = await execute_query(
            "SELECT generate_api_key_v2($1, 'free', 'direct') as result",
            verification['email'],
            fetch="val"
        )
        
        import json
        api_data = json.loads(result)
        
        return {
            "success": True,
            "message": "Email verificata con successo!",
            "api_key": api_data['api_key'],
            "email": verification['email']
        }
