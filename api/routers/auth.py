from fastapi import APIRouter, HTTPException, Query
from api.models.trends import (
    ApiKeyInfo, UserRegistrationRequest, UserRegistrationResponse,
    RapidAPIKeyRequest, RapidAPIKeyResponse, EmailVerificationRequest,
    EmailVerificationResponse, UserInfo, ApiKeyDetailed
)
from api.core.database import execute_query
from api.services.email_service import EmailService
import json

router = APIRouter()

@router.post("/generate-key", response_model=ApiKeyInfo)
async def generate_api_key(
    email: str = Query(..., description="Email per associare la chiave"),
    tier: str = Query("free", description="Tier del piano", enum=["free", "developer", "business", "enterprise"])
):
    """
    🔑 **Genera nuova API Key**
    
    Crea una nuova API key per accedere all'API.
    
    **Piani disponibili:**
    - **Free**: 1.000 chiamate/mese, solo endpoint /global
    - **Developer**: 10.000 chiamate/mese, tutti gli endpoint base
    - **Business**: 50.000 chiamate/mese, include analytics avanzate
    - **Enterprise**: 200.000 chiamate/mese, supporto prioritario
    """
    try:
        # Genera la chiave usando la funzione del database
        new_key = await execute_query(
            "SELECT generate_api_key($1, $2) as key",
            email,
            tier,
            fetch="val"
        )
        
        # Recupera le informazioni della chiave creata
        key_info = await execute_query(
            "SELECT * FROM api_keys WHERE key = $1",
            new_key,
            fetch="one"
        )
        
        return ApiKeyInfo(
            key=new_key,
            tier=key_info['tier'],
            monthly_limit=key_info['monthly_limit'],
            current_usage=0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella generazione della chiave: {str(e)}")

@router.get("/usage", response_model=dict)
async def get_usage_stats(
    api_key: str = Query(..., description="La tua API key")
):
    """
    📊 **Statistiche utilizzo**
    
    Mostra le statistiche di utilizzo della tua API key.
    """
    try:
        # Informazioni base della chiave
        key_info = await execute_query(
            "SELECT * FROM api_keys WHERE key = $1",
            api_key,
            fetch="one"
        )
        
        if not key_info:
            raise HTTPException(status_code=404, detail="API key non trovata")
        
        # Utilizzo del mese corrente
        monthly_usage = await execute_query(
            """
            SELECT COUNT(*) as calls_this_month
            FROM api_usage 
            WHERE api_key = $1 
            AND timestamp >= date_trunc('month', CURRENT_DATE)
            """,
            api_key,
            fetch="one"
        )
        
        # Utilizzo degli ultimi 7 giorni
        weekly_usage = await execute_query(
            """
            SELECT 
                DATE(timestamp) as day,
                COUNT(*) as calls
            FROM api_usage 
            WHERE api_key = $1 
            AND timestamp >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY DATE(timestamp)
            ORDER BY day
            """,
            api_key
        )
        
        weekly_stats = [{"date": row['day'].isoformat(), "calls": row['calls']} for row in weekly_usage]
        
        return {
            "api_key": api_key,
            "tier": key_info['tier'],
            "monthly_limit": key_info['monthly_limit'],
            "calls_this_month": monthly_usage['calls_this_month'],
            "remaining": key_info['monthly_limit'] - monthly_usage['calls_this_month'],
            "total_calls_ever": key_info['usage_count'],
            "last_used": key_info['last_used'].isoformat() if key_info['last_used'] else None,
            "weekly_usage": weekly_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero statistiche: {str(e)}")
