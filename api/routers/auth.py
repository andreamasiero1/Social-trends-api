from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Literal
from api.models.trends import (
    ApiKeyInfo, UserRegistrationRequest, UserRegistrationResponse,
    RapidAPIKeyRequest, RapidAPIKeyResponse, EmailVerificationRequest,
    EmailVerificationResponse, UserInfo, ApiKeyDetailed
)
from api.core.database import execute_query
from api.services.email_service import EmailService
import json

router = APIRouter()


class GenerateKeyRequest(BaseModel):
    """Richiesta per generare API key (accettata nel body JSON del POST)."""
    email: Optional[str] = None
    tier: Optional[Literal["free", "developer", "business", "enterprise"]] = "free"


async def _generate_api_key_core(email: str, tier: str) -> ApiKeyInfo:
    """Logica condivisa per la generazione della chiave con controlli robusti."""
    # Genera la chiave usando la funzione del database
    new_key = await execute_query(
        "SELECT generate_api_key($1, $2) as key",
        email,
        tier,
        fetch="val"
    )

    if not new_key:
        # La funzione DB non ha restituito alcuna chiave
        raise HTTPException(
            status_code=400,
            detail=(
                "Impossibile generare la chiave. Verifica l'email o il piano richiesto. "
                "Per nuovi utenti consigliamo di usare /v1/auth/v2/register con verifica email."
            )
        )

    # Recupera le informazioni della chiave creata
    key_info = await execute_query(
        "SELECT * FROM api_keys WHERE key = $1",
        new_key,
        fetch="one"
    )

    if not key_info:
        # Evita 'NoneType is not subscriptable' e fornisce messaggio chiaro
        raise HTTPException(
            status_code=500,
            detail=(
                "Errore interno: chiave generata ma non reperita a database. "
                "Riprova più tardi o registra l'account tramite /v1/auth/v2/register."
            )
        )

    return ApiKeyInfo(
        key=new_key,
        tier=key_info['tier'],
        monthly_limit=key_info['monthly_limit'],
        current_usage=0
    )

@router.get("/generate-key", response_model=ApiKeyInfo)
async def generate_api_key_get(
    email: str = Query(..., description="Email per associare la chiave"),
    tier: str = Query("free", description="Tier del piano", enum=["free", "developer", "business", "enterprise"])
):
    """
    🔑 Genera nuova API Key (GET)

    Accetta parametri in query string (retrocompatibilità per client che usano GET).
    """
    try:
        return await _generate_api_key_core(email, tier)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella generazione della chiave: {str(e)}")


@router.post("/generate-key", response_model=ApiKeyInfo)
async def generate_api_key_post(
    # Query params opzionali per retrocompatibilità
    email: Optional[str] = Query(None, description="Email per associare la chiave"),
    tier: Optional[str] = Query(None, description="Tier del piano", enum=["free", "developer", "business", "enterprise"]),
    # Body JSON opzionale per i client che lo preferiscono
    body: Optional[GenerateKeyRequest] = None,
):
    """
    🔑 Genera nuova API Key (POST)

    Accetta sia query params sia body JSON. Se forniti entrambi, i query params hanno precedenza.
    """
    try:
        effective_email = email or (body.email if body and body.email else None)
        effective_tier = tier or (body.tier if body and body.tier else "free")

        if not effective_email:
            raise HTTPException(status_code=422, detail="Field 'email' required in query or JSON body")
        if effective_tier not in {"free", "developer", "business", "enterprise"}:
            raise HTTPException(status_code=422, detail="Invalid 'tier'. Use one of: free, developer, business, enterprise")

        return await _generate_api_key_core(effective_email, effective_tier)
    except HTTPException:
        raise
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
