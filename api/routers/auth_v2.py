from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Literal
from api.models.trends import (
    ApiKeyInfo, UserRegistrationRequest, UserRegistrationResponse,
    RapidAPIKeyRequest, RapidAPIKeyResponse, UserInfo, ApiKeyDetailed
)
from api.core.database import execute_query
import json

router = APIRouter()

class GenerateKeyRequestV2(BaseModel):
    email: Optional[str] = None
    tier: Optional[Literal["free", "developer", "business", "enterprise"]] = "free"

async def _generate_api_key_core(email: str, tier: str) -> ApiKeyInfo:
    # Genera la chiave usando la funzione del database
    new_key = await execute_query(
        "SELECT generate_api_key($1, $2) as key",
        email,
        tier,
        fetch="val"
    )

    if not new_key:
        raise HTTPException(
            status_code=400,
            detail=(
                "Impossibile generare la chiave. Verifica l'email o il piano richiesto. "
                "Per nuovi utenti usa /v1/auth/v2/register con verifica email."
            )
        )

    # Recupera le informazioni della chiave creata
    key_info = await execute_query(
        "SELECT * FROM api_keys WHERE key = $1",
        new_key,
        fetch="one"
    )

    if not key_info:
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

@router.post("/register", response_model=dict)
async def register_user(request: UserRegistrationRequest):
    """
    � **Registrazione Utente Istantanea**
    
    Registra un nuovo utente e genera immediatamente l'API key.
    Perfetto per RapidAPI - nessuna verifica email richiesta!
    
    **Piani disponibili:**
    - **Free**: 1.000 chiamate/mese
    - **Developer**: 10.000 chiamate/mese  
    - **Business**: 50.000 chiamate/mese
    - **Enterprise**: 200.000 chiamate/mese
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
                "message": "Email già registrata. Se hai perso l'API key, usa l'endpoint /keys/{email} per recuperarla.",
                "api_key": None
            }
        
        # Genera direttamente l'API key
        result = await execute_query(
            "SELECT generate_api_key_v2($1, $2, 'instant') as result",
            request.email,
            request.tier or "free",
            fetch="val"
        )
        
        if not result:
            raise HTTPException(
                status_code=500, 
                detail="Errore nel database: funzione generate_api_key_v2 non disponibile o non configurata correttamente"
            )
        
        try:
            api_data = json.loads(result)
        except (json.JSONDecodeError, TypeError) as e:
            raise HTTPException(
                status_code=500,
                detail=f"Errore nella risposta del database: {str(e)}"
            )
        
        # Controlla se la funzione ha restituito un errore
        if not api_data.get("success", False):
            error_msg = api_data.get("message", "Errore sconosciuto nella generazione API key")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Marca utente come verificato immediatamente
        await execute_query(
            "UPDATE users SET is_email_verified = TRUE WHERE email = $1",
            request.email
        )
        
        return {
            "status": "success",
            "message": "🎉 API key generata con successo!",
            "api_key": api_data['api_key'],
            "tier": api_data.get('tier', request.tier or "free"),
            "email": request.email,
            "monthly_limit": api_data.get('monthly_limit', _get_monthly_limit(request.tier or "free")),
            "note": "⚠️ Salva questa API key in un posto sicuro. Non sarà possibile recuperarla se persa."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella generazione API key: {str(e)}")

def _get_monthly_limit(tier: str) -> int:
    """Restituisce il limite mensile per il tier"""
    limits = {
        "free": 1000,
        "developer": 10000, 
        "business": 50000,
        "enterprise": 200000
    }
    return limits.get(tier, 1000)



@router.post("/rapidapi/provision", response_model=RapidAPIKeyResponse)
async def provision_rapidapi_key(request: RapidAPIKeyRequest):
    """
    🚀 **Provisioning API Key per RapidAPI**
    
    Endpoint interno per RapidAPI per creare API keys automaticamente
    quando un utente si iscrive a un piano a pagamento.
    """
    try:
        # Usa la funzione del database per creare la chiave
        result = await execute_query(
            "SELECT generate_api_key_v2($1, $2, 'rapidapi', $3) as result",
            request.email,
            request.tier,
            request.rapidapi_user_id,
            fetch="val"
        )
        
        if not result:
            raise HTTPException(
                status_code=500, 
                detail="Errore nel database: funzione generate_api_key_v2 non disponibile"
            )
        
        try:
            api_data = json.loads(result)
        except (json.JSONDecodeError, TypeError) as e:
            raise HTTPException(
                status_code=500,
                detail=f"Errore nella risposta del database: {str(e)}"
            )
        
        if not api_data.get("success", False):
            error_msg = api_data.get("message", "Errore nella generazione API key per RapidAPI")
            raise HTTPException(status_code=400, detail=error_msg)
        
        return RapidAPIKeyResponse(
            api_key=api_data['api_key'],
            user_id=api_data['user_id'],
            tier=api_data['tier'],
            monthly_limit=api_data['monthly_limit']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel provisioning RapidAPI: {str(e)}")

@router.get("/generate-key", response_model=ApiKeyInfo)
async def generate_api_key_get(
    email: str = Query(..., description="Email per associare la chiave"),
    tier: str = Query("free", description="Tier del piano", enum=["free", "developer", "business", "enterprise"])
):
    """
    🔑 **Genera nuova API Key (DEPRECATO)** - GET

    Compatibilità per client che inviano parametri in query. Consigliamo POST /v1/auth/v2/register.
    """
    try:
        return await _generate_api_key_core(email, tier)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella generazione della chiave: {str(e)}")

@router.post("/generate-key", response_model=ApiKeyInfo)
async def generate_api_key_post(
    email: Optional[str] = Query(None, description="Email per associare la chiave"),
    tier: Optional[str] = Query(None, description="Tier del piano", enum=["free", "developer", "business", "enterprise"]),
    body: Optional[GenerateKeyRequestV2] = None,
):
    """
    🔑 **Genera nuova API Key (DEPRECATO)** - POST

    Accetta query params o body JSON (i query params hanno precedenza). Consigliamo di usare
    POST /v1/auth/v2/register per nuovi utenti.
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

@router.get("/my-account", response_model=dict)
async def get_account_info(
    api_key: str = Query(..., description="La tua API key")
):
    """
    👤 **Informazioni Account**
    
    Mostra tutte le informazioni del tuo account e delle tue API keys.
    """
    try:
        # Trova l'utente tramite la chiave API
        user_info = await execute_query(
            """
            SELECT u.*, ak.key, ak.tier, ak.monthly_limit, ak.usage_count, ak.source
            FROM users u
            JOIN api_keys ak ON u.id = ak.user_id
            WHERE ak.key = $1
            """,
            api_key,
            fetch="one"
        )
        
        if not user_info:
            raise HTTPException(status_code=404, detail="API key non trovata")
        
        # Tutte le API keys dell'utente
        all_keys = await execute_query(
            """
            SELECT key, tier, monthly_limit, usage_count, source, is_active, created_at, last_used
            FROM api_keys
            WHERE user_id = (SELECT user_id FROM api_keys WHERE key = $1)
            ORDER BY created_at DESC
            """,
            api_key
        )
        
        return {
            "user": {
                "id": user_info['id'],
                "email": user_info['email'],
                "is_email_verified": user_info['is_email_verified'],
                "registration_source": user_info['registration_source'],
                "created_at": user_info['created_at'].isoformat()
            },
            "api_keys": [
                {
                    "key": key['key'][:10] + "..." + key['key'][-4:],  # Maschera la chiave
                    "full_key": key['key'] if key['key'] == api_key else None,  # Mostra completa solo quella corrente
                    "tier": key['tier'],
                    "monthly_limit": key['monthly_limit'],
                    "total_usage": key['usage_count'],
                    "source": key['source'],
                    "is_active": key['is_active'],
                    "created_at": key['created_at'].isoformat(),
                    "last_used": key['last_used'].isoformat() if key['last_used'] else None
                }
                for key in all_keys
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero account: {str(e)}")


@router.get("/keys/{email}")
async def get_user_api_keys(email: str):
    """
    Recupera tutte le API key attive per un utente
    Utile per RapidAPI quando un utente perde la chiave
    """
    try:
        user = await execute_query(
            "SELECT id, email, is_email_verified FROM users WHERE email = $1",
            email,
            fetch="one"
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="Email non trovata nel sistema")
        
        # Recupera tutte le chiavi attive
        api_keys = await execute_query(
            """
            SELECT api_key, tier, is_active, created_at, 
                   monthly_requests, last_used_at
            FROM api_keys 
            WHERE user_id = $1 AND is_active = TRUE
            ORDER BY created_at DESC
            """,
            user['id']
        )
        
        if not api_keys:
            return {
                "status": "not_found",
                "message": "Nessuna API key attiva trovata per questa email",
                "email": email,
                "suggestion": "Usa /register-instant per generare una nuova chiave"
            }
        
        return {
            "status": "success",
            "email": email,
            "total_keys": len(api_keys),
            "keys": [
                {
                    "api_key": key['api_key'],
                    "tier": key['tier'],
                    "created_at": key['created_at'].isoformat() if key['created_at'] else None,
                    "monthly_requests": key['monthly_requests'],
                    "monthly_limit": _get_monthly_limit(key['tier']),
                    "last_used": key['last_used_at'].isoformat() if key['last_used_at'] else "Mai usata"
                }
                for key in api_keys
            ],
            "note": "⚠️ Proteggi queste API key. Non condividerle pubblicamente."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero chiavi: {str(e)}")
