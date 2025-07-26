from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional
from datetime import datetime
from api.services.trend_service import TrendService
from api.models.trends import (
    TrendResponse, PlatformTrendResponse, CountryTrendResponse,
    KeywordAnalysis, RelatedHashtagsResponse
)
from api.core.security import get_current_api_key, require_tier

router = APIRouter()
trend_service = TrendService()

@router.get("/global", response_model=TrendResponse)
async def get_global_trends(
    limit: int = Query(10, ge=1, le=100, description="Numero massimo di trend da restituire"),
    api_key_info: dict = Depends(get_current_api_key)
):
    """
    🌍 **Trend Globali**
    
    Restituisce i trend più popolari aggregati da TikTok e Instagram.
    Disponibile anche nel piano Free.
    """
    try:
        results = await trend_service.get_global_trends(limit)
        
        return TrendResponse(
            last_updated=datetime.now(),
            total_trends=len(results),
            trends=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero trend globali: {str(e)}")

@router.get("/platform", response_model=PlatformTrendResponse)
async def get_platform_trends(
    source: str = Query(..., description="Piattaforma social da interrogare", enum=["tiktok", "instagram"]),
    limit: int = Query(20, ge=1, le=50, description="Numero massimo di trend da restituire"),
    api_key_info: dict = Depends(require_tier("developer"))
):
    """
    📱 **Trend per Piattaforma**
    
    Restituisce i trend specifici per una singola piattaforma social.
    Richiede piano Developer o superiore.
    """
    try:
        if source == "tiktok":
            results = await trend_service.tiktok_service.get_trends(limit, use_db=False)
        elif source == "instagram":
            results = await trend_service.instagram_service.get_trends(limit, use_db=False)
        else:
            raise ValueError("Piattaforma non supportata")
        
        return PlatformTrendResponse(
            platform=source,
            last_updated=datetime.now(),
            total_trends=len(results),
            trends=results
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero trend {source}: {str(e)}")

@router.get("/country", response_model=CountryTrendResponse)
async def get_country_trends(
    code: str = Query(..., min_length=2, max_length=2, description="Codice paese ISO 3166-1 alpha-2 (es: IT, US, GB)"),
    limit: int = Query(10, ge=1, le=50, description="Numero massimo di trend da restituire"),
    api_key_info: dict = Depends(require_tier("business"))
):
    """
    🌐 **Trend per Paese**
    
    Restituisce i trend specifici per un paese.
    Richiede piano Business o superiore.
    """
    try:
        results = await trend_service.get_country_trends(code, limit)
        
        return CountryTrendResponse(
            country=code.upper(),
            last_updated=datetime.now(),
            trends=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero trend per {code}: {str(e)}")

@router.get("/analysis/keyword", response_model=KeywordAnalysis)
async def analyze_keyword_mentions(
    keyword: str = Query(..., min_length=1, description="Parola chiave o hashtag da analizzare"),
    hours: int = Query(24, ge=1, le=168, description="Ore precedenti da analizzare (max 7 giorni)"),
    api_key_info: dict = Depends(require_tier("developer"))
):
    """
    🔍 **Analisi Keyword**
    
    Analizza una specifica parola chiave o hashtag fornendo:
    - Volume totale di menzioni
    - Distribuzione per piattaforma  
    - Sentiment medio
    - Timeline oraria
    
    Richiede piano Developer o superiore.
    """
    try:
        results = await trend_service.analyze_keyword(keyword, hours)
        
        return KeywordAnalysis(
            keyword=keyword,
            total_mentions=results["total_mentions"],
            platforms=results["platforms"],
            sentiment_avg=results["sentiment_avg"],
            timeline=results["timeline"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nell'analisi di '{keyword}': {str(e)}")

@router.get("/hashtags/related", response_model=RelatedHashtagsResponse)
async def get_related_hashtags(
    hashtag: str = Query(..., description="Hashtag di partenza (con o senza #)"),
    limit: int = Query(10, ge=1, le=30, description="Numero massimo di hashtag correlati"),
    api_key_info: dict = Depends(require_tier("developer"))
):
    """
    🔗 **Hashtag Correlati**
    
    Trova hashtag correlati a quello fornito basandosi sulla co-occorrenza
    nei trend e nelle menzioni.
    
    Richiede piano Developer o superiore.
    """
    try:
        # Pulisci l'hashtag (rimuovi # se presente)
        clean_hashtag = hashtag.lstrip('#')
        
        results = await trend_service.get_related_hashtags(clean_hashtag, limit)
        
        return RelatedHashtagsResponse(
            hashtag=f"#{clean_hashtag}",
            related_hashtags=results,
            last_updated=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella ricerca hashtag correlati a '{hashtag}': {str(e)}")
