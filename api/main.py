from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from api.core.config import settings
from api.routers import trends, auth, auth_v2

# Crea l'applicazione FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware per timing e logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include i router
app.include_router(
    trends.router,
    prefix=f"{settings.API_V1_STR}/trends",
    tags=["📈 Trends"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["🔑 Authentication"],
)

# Nuovo router auth con funzionalità migliorate
app.include_router(
    auth_v2.router,
    prefix=f"{settings.API_V1_STR}/auth/v2",
    tags=["🔐 Authentication V2"],
)

@app.get("/", tags=["🏠 Info"])
async def root():
    """
    🚀 **Welcome to Social Trends API**
    
    API per aggregare e analizzare trend da TikTok e Instagram in tempo reale.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.PROJECT_DESCRIPTION,
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "trends_global": f"{settings.API_V1_STR}/trends/global",
            "trends_platform": f"{settings.API_V1_STR}/trends/platform",
            "trends_country": f"{settings.API_V1_STR}/trends/country",
            "keyword_analysis": f"{settings.API_V1_STR}/trends/analysis/keyword",
            "related_hashtags": f"{settings.API_V1_STR}/trends/hashtags/related",
            "generate_api_key": f"{settings.API_V1_STR}/auth/generate-key",
            "usage_stats": f"{settings.API_V1_STR}/auth/usage",
            "register_v2": f"{settings.API_V1_STR}/auth/v2/register",
            "my_account": f"{settings.API_V1_STR}/auth/v2/my-account",
            "api_keys_by_email": f"{settings.API_V1_STR}/auth/v2/keys/{{email}}"
        },
        "supported_platforms": ["tiktok", "instagram"],
        "plans": {
            "free": "1,000 calls/month - Global trends only",
            "developer": "10,000 calls/month - All basic endpoints",
            "business": "50,000 calls/month - Advanced analytics",
            "enterprise": "200,000 calls/month - Priority support"
        }
    }

@app.get("/health", tags=["🏠 Info"])
async def health_check():
    """
    ✅ **Health Check**
    
    Verifica che l'API sia operativa.
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": time.time()
    }

@app.get("/health/detailed", tags=["🏠 Info"])
async def detailed_health_check():
    """
    🔍 **Detailed Health Check**
    
    Verifica l'API e la connessione al database.
    """
    from api.core.database import execute_query
    
    result = {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": time.time(),
        "database": "unknown"
    }
    
    try:
        # Test semplice del database
        db_result = await execute_query("SELECT 1 as test", fetch="val")
        if db_result == 1:
            result["database"] = "connected"
        else:
            result["database"] = "error"
            result["status"] = "degraded"
    except Exception as e:
        result["database"] = f"error: {str(e)}"
        result["status"] = "degraded"
    
    return result

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint non trovato",
            "message": "Controlla la documentazione: /docs",
            "available_endpoints": "/v1/trends/global, /v1/trends/platform, /v1/trends/country"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Errore interno del server",
            "message": "Riprova più tardi o contatta il supporto"
        }
    )
