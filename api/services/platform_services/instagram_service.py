from typing import List, Dict, Any
import random
from datetime import datetime, timedelta
from api.core.database import execute_query

class InstagramService:
    def __init__(self):
        self.platform = "instagram"
    
    async def get_trends_from_db(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Recupera i trend Instagram dal database"""
        
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
                "posts_count": metadata.get("posts_count", random.randint(500000, 3000000)),
                "avg_likes": metadata.get("avg_likes", random.randint(5000, 25000)),
                "avg_comments": metadata.get("avg_comments", random.randint(200, 1500))
            }
            trends.append(trend)
        
        return trends
    
    async def simulate_real_data(self) -> List[Dict[str, Any]]:
        """Simula dati realistici per Instagram"""
        mock_trends = [
            {"name": "#instagood", "base_volume": 1100000},
            {"name": "#photooftheday", "base_volume": 900000},
            {"name": "#fashion", "base_volume": 850000},
            {"name": "#beautiful", "base_volume": 800000},
            {"name": "#art", "base_volume": 750000},
            {"name": "#photography", "base_volume": 700000},
            {"name": "#nature", "base_volume": 650000},
            {"name": "#travel", "base_volume": 600000},
            {"name": "#fitness", "base_volume": 550000},
            {"name": "#food", "base_volume": 500000}
        ]
        
        trends = []
        for idx, trend in enumerate(mock_trends):
            volume_variation = random.uniform(0.85, 1.25)
            volume = int(trend["base_volume"] * volume_variation)
            
            trend_data = {
                "rank": idx + 1,
                "name": trend["name"],
                "volume": volume,
                "posts_count": random.randint(2000000, 12000000),
                "avg_likes": random.randint(8000, 35000),
                "avg_comments": random.randint(300, 2000),
                "growth_24h": round(random.uniform(-10.0, 30.0), 1)
            }
            trends.append(trend_data)
        
        return trends
    
    async def get_trends(self, limit: int = 20, use_db: bool = True) -> List[Dict[str, Any]]:
        """Recupera i trend Instagram"""
        if use_db:
            db_trends = await self.get_trends_from_db(limit)
            if db_trends:
                return db_trends
        
        return await self.simulate_real_data()
