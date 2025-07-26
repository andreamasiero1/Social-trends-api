import uvicorn
from api.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # Auto-reload durante sviluppo
        log_level="info"
    )
