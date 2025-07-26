from fastapi import HTTPException, Security, Depends, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.database import get_db, execute_query
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
        # Cerca la chiave nel database
        key_info = await execute_query(
            "SELECT * FROM api_keys WHERE key = $1 AND is_active = TRUE",
            api_key,
            fetch="one"
        )
        
        if not key_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key non valida"
            )
        
        # Controlla il rate limiting mensile
        first_day_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_usage = await execute_query(
            "SELECT COUNT(*) FROM api_usage WHERE api_key = $1 AND timestamp >= $2",
            api_key,
            first_day_month,
            fetch="val"
        ) or 0
        
        if monthly_usage >= key_info['monthly_limit']:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Limite mensile di {key_info['monthly_limit']} richieste superato. Upgrade il tuo piano."
            )
        
        # Registra l'utilizzo
        await execute_query(
            "INSERT INTO api_usage (api_key, endpoint, timestamp) VALUES ($1, $2, $3)",
            api_key,
            "api_call",  # Sarà aggiornato da un middleware
            datetime.now()
        )
        
        # Aggiorna last_used
        await execute_query(
            "UPDATE api_keys SET last_used = $1, usage_count = usage_count + 1 WHERE key = $2",
            datetime.now(),
            api_key
        )
        
        return {
            "key": api_key,
            "tier": key_info['tier'],
            "monthly_limit": key_info['monthly_limit'],
            "monthly_usage": monthly_usage + 1,
            "user_email": key_info['user_email']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Database connection error in auth: {e}")
        # Per testing, usiamo chiavi hardcoded
        test_keys = {
            "demo-key-12345": {"tier": "free", "monthly_limit": 1000, "user_email": "demo@example.com"},
            "dev-key-67890": {"tier": "developer", "monthly_limit": 10000, "user_email": "dev@example.com"},
            "test-key-andrea": {"tier": "business", "monthly_limit": 50000, "user_email": "andrea@test.com"}
        }
        
        if api_key in test_keys:
            key_data = test_keys[api_key]
            return {
                "key": api_key,
                "tier": key_data["tier"],
                "monthly_limit": key_data["monthly_limit"],
                "monthly_usage": 1,
                "user_email": key_data["user_email"]
            }
        else:
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
