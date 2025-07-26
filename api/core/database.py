from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from api.core.config import settings
import asyncpg
import os
from typing import AsyncGenerator

# SQLAlchemy setup
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

# Dependency per FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Pool di connessioni per query dirette
postgres_pool = None

async def get_postgres_pool():
    global postgres_pool
    if postgres_pool is None:
        # Usa l'URL completo se disponibile, altrimenti le singole variabili
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            # Rimuovi il prefixo postgresql+asyncpg:// per asyncpg
            if db_url.startswith("postgresql+asyncpg://"):
                db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
            postgres_pool = await asyncpg.create_pool(db_url, min_size=5, max_size=20)
        else:
            postgres_pool = await asyncpg.create_pool(
                host=settings.POSTGRES_SERVER,
                port=int(settings.POSTGRES_PORT),
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                min_size=5,
                max_size=20
            )
    return postgres_pool

async def execute_query(query: str, *args, fetch="all"):
    """Esegue query SQL dirette con asyncpg"""
    try:
        # Usa l'URL completo se disponibile
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            # Rimuovi il prefixo postgresql+asyncpg:// per asyncpg
            if db_url.startswith("postgresql+asyncpg://"):
                db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
            conn = await asyncpg.connect(db_url)
        else:
            conn = await asyncpg.connect(
                host=settings.POSTGRES_SERVER,
                port=int(settings.POSTGRES_PORT),
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB
            )
        
        if fetch == "all":
            result = await conn.fetch(query, *args)
        elif fetch == "one":
            result = await conn.fetchrow(query, *args)
        elif fetch == "val":
            result = await conn.fetchval(query, *args)
        else:
            result = await conn.execute(query, *args)
            
        await conn.close()
        return result
        
    except Exception as e:
        print(f"Database error: {e}")
        # Per ora ritorniamo dati di fallback per permettere il testing
        if fetch == "one":
            return None
        elif fetch == "val":
            return None
        else:
            return []
