from fastapi import HTTPException, Security, Depends, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.database import get_db, execute_query
from api.core.config import settings
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_api_key(
    api_key: Optional[str] = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Valida l'API key e restituisce le informazioni"""
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key richiesta. Aggiungi header X-API-Key"
        )
    
    try:
        # Prova la connessione al database
        key_info = await execute_query(
            "SELECT * FROM api_keys WHERE key = $1 AND is_active = TRUE",
            api_key,
            fetch="one"
        )
        
        if not key_info:
            # In demo mode, accetta chiavi di test anche se la query non ha restituito risultati
            if settings.ACCEPT_TEST_KEYS:
                test_keys = {
                    'test_free_key_123': {'user_email': 'test@example.com', 'tier': 'free'},
                    'test_developer_key_456': {'user_email': 'developer@example.com', 'tier': 'developer'},
                    'test_enterprise_key_789': {'user_email': 'enterprise@example.com', 'tier': 'enterprise'}
                }
                if api_key in test_keys:
                    tier = test_keys[api_key]['tier']
                    return {
                        "api_key": api_key,
                        "user_email": test_keys[api_key]['user_email'],
                        "tier": tier,
                        "monthly_usage": 0,
                        "monthly_limit": tier_limits.get(tier, settings.FREE_TIER_MONTHLY_LIMIT)
                    }
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key non valida"
            )
        
        # Controlla il rate limiting mensile basato sul tier
        tier_limits = {
            'free': settings.FREE_TIER_MONTHLY_LIMIT,
            'developer': settings.DEVELOPER_TIER_MONTHLY_LIMIT,
            'business': settings.BUSINESS_TIER_MONTHLY_LIMIT,
            'enterprise': settings.ENTERPRISE_TIER_MONTHLY_LIMIT
        }
        
        monthly_limit = tier_limits.get(key_info['tier'], 1000)
        first_day_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_usage = await execute_query(
            "SELECT COUNT(*) FROM api_usage WHERE api_key = $1 AND timestamp >= $2",
            api_key,
            first_day_month,
            fetch="val"
        ) or 0
        
        if monthly_usage >= monthly_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Limite mensile di {monthly_limit} richieste superato per il tier {key_info['tier']}. Upgrade il tuo piano."
            )
        
        # Registra l'utilizzo
        try:
            await execute_query(
                "INSERT INTO api_usage (api_key, endpoint, timestamp) VALUES ($1, $2, $3)",
                api_key,
                "api_request",
                datetime.now(),
                fetch="none"
            )
            
            # Aggiorna statistiche dell'API key
            await execute_query(
                "UPDATE api_keys SET last_used = $1, usage_count = usage_count + 1 WHERE key = $2",
                datetime.now(),
                api_key,
                fetch="none"
            )
        except Exception as log_error:
            print(f"Errore logging utilizzo: {log_error}")
        
        return {
            "api_key": api_key,
            "user_email": key_info['user_email'],
            "tier": key_info['tier'],
            "monthly_usage": monthly_usage,
            "monthly_limit": monthly_limit
        }
        
    except HTTPException:
        # Re-raise le eccezioni HTTP (API key invalida, rate limit, etc.)
        raise
    except Exception as e:
        print(f"Database connection error in auth: {e}")
        # Sistema di fallback per le API key di test (abilitabile via settings)
        if settings.ACCEPT_TEST_KEYS:
            test_keys = {
                'test_free_key_123': {'user_email': 'test@example.com', 'tier': 'free'},
                'test_developer_key_456': {'user_email': 'developer@example.com', 'tier': 'developer'},
                'test_enterprise_key_789': {'user_email': 'enterprise@example.com', 'tier': 'enterprise'}
            }
            if api_key in test_keys:
                print(f"Usando fallback per API key di test: {api_key}")
                tier = test_keys[api_key]['tier']
                return {
                    "api_key": api_key,
                    "user_email": test_keys[api_key]['user_email'],
                    "tier": tier,
                    "monthly_usage": 0,
                    "monthly_limit": tier_limits.get(tier, settings.FREE_TIER_MONTHLY_LIMIT)
                }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key non valida"
        )

def require_tier(minimum_tier: str):
    """Decorator per richiedere un tier minimo"""
    tier_hierarchy = {"free": 0, "developer": 1, "business": 2, "enterprise": 3}
    
    def dependency(api_key_info: Dict[str, Any] = Depends(get_current_api_key)):
        current_tier_level = tier_hierarchy.get(api_key_info["tier"], 0)
        required_tier_level = tier_hierarchy.get(minimum_tier, 0)
        
        if current_tier_level < required_tier_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Questo endpoint richiede almeno il piano {minimum_tier.title()}"
            )
        
        return api_key_info
    
    return dependency
