import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Info del progetto
    PROJECT_NAME: str = "Social Trends API"
    PROJECT_DESCRIPTION: str = "API per aggregare trend da TikTok e Instagram"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/v1"
    
    # Configurazione server
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres123")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "social_trends")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis per Celery
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    CELERY_BROKER_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # API Keys esterne (per ora vuote)
    TIKTOK_API_KEY: str = os.getenv("TIKTOK_API_KEY", "")
    INSTAGRAM_API_KEY: str = os.getenv("INSTAGRAM_API_KEY", "")
    
    # Sicurezza
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
    
    # Rate limiting
    FREE_TIER_MONTHLY_LIMIT: int = 1000
    DEVELOPER_TIER_MONTHLY_LIMIT: int = 10000
    
    class Config:
        env_file = ".env"

settings = Settings()
