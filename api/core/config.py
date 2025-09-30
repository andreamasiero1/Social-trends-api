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
    
    # Database - supporta sia DATABASE_URL che singole variabili
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")  # Legge da environment
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres123")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "social_trends")
    
    def get_database_url(self) -> str:
        # Se DATABASE_URL è configurato nel .env, usalo
        if self.DATABASE_URL:
            # Sostituisci postgresql:// con postgresql+asyncpg:// per asyncpg
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            return self.DATABASE_URL
        # Altrimenti costruisci l'URL dalle singole variabili
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
    BUSINESS_TIER_MONTHLY_LIMIT: int = 50000
    ENTERPRISE_TIER_MONTHLY_LIMIT: int = 200000

    # Demo / Test mode
    ACCEPT_TEST_KEYS: bool = os.getenv("ACCEPT_TEST_KEYS", "false").lower() == "true"
    
    # Email Configuration (opzionale - per invio email di verifica)
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "noreply@social-trends-api.com")
    
    # URL base per i link di verifica
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    
    class Config:
        env_file = ".env"

settings = Settings()
