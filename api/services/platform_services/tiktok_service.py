from typing import List, Dict, Any
import random
from datetime import datetime, timedelta
from api.core.database import execute_query
import asyncio

class TikTokService:
    def __init__(self):
        self.platform = "tiktok"
    
    async def get_trends_from_db(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Recupera i trend TikTok dal database"""
        
        # Query per i trend delle ultime 24 ore
        query = """
        SELECT 
            name,
            AVG(volume)::int as avg_volume,
            MAX(volume) as max_volume,
            COUNT(*) as data_points,
            metadata
        FROM trends 
        WHERE platform = $1 
        AND time > NOW() - INTERVAL '24 hours'
        GROUP BY name, metadata
        ORDER BY avg_volume DESC
        LIMIT $2
        """
        
        results = await execute_query(query, self.platform, limit)
        
        trends = []
        for idx, row in enumerate(results):
            metadata = row['metadata'] or {}
            
            trend = {
                "rank": idx + 1,
                "name": row['name'],
                "volume": row['avg_volume'],
                "max_volume_24h": row['max_volume'],
                "data_points": row['data_points'],
                "videos_count": metadata.get("videos_count", random.randint(100000, 5000000)),
                "engagement_rate": metadata.get("engagement_rate", round(random.uniform(3.0, 15.0), 1)),
                "hashtag_views": metadata.get("hashtag_views", random.randint(10000000, 500000000))
            }
            trends.append(trend)
        
        return trends
    
    async def simulate_real_data(self) -> List[Dict[str, Any]]:
        """Simula dati realistici per TikTok"""
        mock_trends = [
            {"name": "#fyp", "base_volume": 1200000},
            {"name": "#viral", "base_volume": 950000},
            {"name": "#dance", "base_volume": 800000},
            {"name": "#comedy", "base_volume": 750000},
            {"name": "#music", "base_volume": 700000},
            {"name": "#trend", "base_volume": 650000},
            {"name": "#funny", "base_volume": 600000},
            {"name": "#tiktokmademebuyit", "base_volume": 550000},
            {"name": "#duet", "base_volume": 500000},
            {"name": "#food", "base_volume": 450000}
        ]
        
        trends = []
        for idx, trend in enumerate(mock_trends):
            # Aggiungi variazione casuale realistica
            volume_variation = random.uniform(0.8, 1.3)
            volume = int(trend["base_volume"] * volume_variation)
            
            trend_data = {
                "rank": idx + 1,
                "name": trend["name"],
                "volume": volume,
                "videos_count": random.randint(1000000, 8000000),
                "engagement_rate": round(random.uniform(5.5, 14.2), 1),
                "hashtag_views": random.randint(50000000, 800000000),
                "growth_24h": round(random.uniform(-15.0, 45.0), 1)
            }
            trends.append(trend_data)
        
        return trends
    
    async def get_trends(self, limit: int = 20, use_db: bool = True) -> List[Dict[str, Any]]:
        """Recupera i trend TikTok"""
        if use_db:
            db_trends = await self.get_trends_from_db(limit)
            if db_trends:
                return db_trends
        
        # Fallback a dati simulati
        return await self.simulate_real_data()
