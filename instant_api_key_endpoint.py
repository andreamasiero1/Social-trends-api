"""
Endpoint alternativo per generazione API key immediata
Aggiungere in api/routers/auth_v2.py o creare nuovo file
"""

@router.post("/register-instant")
async def register_instant_api_key(request: UserRegistrationRequest):
    """
    Registrazione con API key immediata - perfetto per RapidAPI
    Non richiede verifica email
    """
    try:
        # Verifica se email già esiste
        existing_user = await execute_query(
            "SELECT id FROM users WHERE email = $1",
            request.email,
            fetch="one"
        )
        
        if existing_user:
            return {
                "status": "error",
                "message": "Email già registrata. Se hai perso l'API key, contatta il supporto.",
                "api_key": None
            }
        
        # Genera direttamente l'API key
        result = await execute_query(
            "SELECT generate_api_key_v2($1, $2, 'instant') as result",
            request.email,
            request.tier or "free",
            fetch="val"
        )
        
        import json
        api_data = json.loads(result)
        
        # Marca utente come verificato immediatamente
        await execute_query(
            "UPDATE users SET is_email_verified = TRUE WHERE email = $1",
            request.email
        )
        
        return {
            "status": "success",
            "message": "🎉 API key generata con successo!",
            "api_key": api_data['api_key'],
            "tier": request.tier or "free",
            "email": request.email,
            "note": "Salva questa API key in un posto sicuro. Non sarà possibile recuperarla."
        }
        
    except Exception as e:
        logger.error(f"Errore nella generazione API key instant: {str(e)}")
        return {
            "status": "error", 
            "message": "Errore interno del server",
            "api_key": None
        }