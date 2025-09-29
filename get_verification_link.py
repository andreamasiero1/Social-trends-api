#!/usr/bin/env python3
"""
Script per recuperare il link di verifica per un utente specifico
"""
import asyncio
import asyncpg
import os
from urllib.parse import urlparse

async def get_verification_link(email: str):
    """Recupera il link di verifica dal database"""
    
    # Ottieni URL database dall'ambiente
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL non configurato nel file .env")
        return None
    
    try:
        # Connetti al database
        conn = await asyncpg.connect(database_url)
        
        # Query per recuperare il token
        query = """
        SELECT 
            u.email,
            ev.token,
            ev.expires_at,
            ev.created_at
        FROM email_verifications ev
        JOIN users u ON ev.user_id = u.id
        WHERE u.email = $1 
        AND ev.verified_at IS NULL 
        AND ev.expires_at > NOW()
        ORDER BY ev.created_at DESC
        LIMIT 1
        """
        
        result = await conn.fetchrow(query, email)
        
        if result:
            token = result['token']
            expires_at = result['expires_at']
            created_at = result['created_at']
            verification_url = f"https://social-trends-api.onrender.com/v1/auth/v2/verify-email?token={token}"
            
            print("✅ TOKEN DI VERIFICA TROVATO!")
            print("=" * 50)
            print(f"📧 Email: {email}")
            print(f"🕐 Creato: {created_at}")
            print(f"⏰ Scade: {expires_at}")
            print(f"🔗 Link di verifica:")
            print(f"   {verification_url}")
            print("=" * 50)
            print("\n💡 Copia e incolla il link nel browser per verificare l'email")
            return verification_url
        else:
            print(f"❌ Nessun token di verifica attivo trovato per {email}")
            print("Possibili cause:")
            print("• Token già utilizzato")
            print("• Token scaduto")
            print("• Email non registrata")
            return None
            
    except Exception as e:
        print(f"❌ Errore connessione database: {e}")
        return None
    finally:
        if 'conn' in locals():
            await conn.close()

async def main():
    """Main function"""
    email = "yreq@honesthirianinda.net"
    
    print(f"🔍 Recuperando link di verifica per: {email}")
    print("=" * 60)
    
    link = await get_verification_link(email)
    
    if not link:
        print("\n🛠️ COSA FARE:")
        print("1. Assicurati che DATABASE_URL sia configurato nel .env")
        print("2. Controlla che l'email sia corretta")
        print("3. Se il token è scaduto, registra di nuovo l'utente")

if __name__ == "__main__":
    asyncio.run(main())