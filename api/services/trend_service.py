from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from api.services.platform_services.tiktok_service import TikTokService
from api.services.platform_services.instagram_service import InstagramService
from api.core.database import execute_query

class TrendService:
    def __init__(self):
        self.tiktok_service = TikTokService()
        self.instagram_service = InstagramService()
    
    async def get_global_trends(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Combina trend da tutte le piattaforme"""
        
        # Per ora usiamo solo dati simulati
        tiktok_trends = await self.tiktok_service.get_trends(limit=limit, use_db=False)
        instagram_trends = await self.instagram_service.get_trends(limit=limit, use_db=False)
        
        # Combina e normalizza
        all_trends = []
        
        # Aggiungi trend TikTok
        for trend in tiktok_trends:
            all_trends.append({
                "name": trend["name"],
                "volume": trend["volume"],
                "platforms": ["tiktok"],
                "growth_percentage": trend.get("growth_24h", 0.0)
            })
        
        # Aggiungi trend Instagram
        for trend in instagram_trends:
            # Cerca se questo trend esiste già (stesso hashtag da TikTok)
            existing = next((t for t in all_trends if t["name"] == trend["name"]), None)
            
            if existing:
                # Combina i dati
                existing["volume"] += trend["volume"]
                existing["platforms"].append("instagram")
                existing["growth_percentage"] = (existing["growth_percentage"] + trend.get("growth_24h", 0.0)) / 2
            else:
                all_trends.append({
                    "name": trend["name"],
                    "volume": trend["volume"],
                    "platforms": ["instagram"],
                    "growth_percentage": trend.get("growth_24h", 0.0)
                })
        
        # Ordina per volume totale
        all_trends.sort(key=lambda x: x["volume"], reverse=True)
        
        # Aggiungi rank e limita i risultati
        final_trends = []
        for idx, trend in enumerate(all_trends[:limit]):
            final_trends.append({
                "rank": idx + 1,
                "name": trend["name"],
                "volume": trend["volume"],
                "growth_percentage": round(trend["growth_percentage"], 1),
                "platforms": trend["platforms"]
            })
        
        return final_trends
    
    async def get_country_trends(self, country_code: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recupera trend per paese specifico con fallback intelligente"""
        
        # Prima prova a cercare trend specifici per paese nel database
        query = """
        SELECT 
            name,
            SUM(volume) as total_volume,
            array_agg(DISTINCT platform) as platforms,
            AVG(
                CASE 
                    WHEN LAG(volume) OVER (PARTITION BY name ORDER BY time) IS NOT NULL 
                    THEN ((volume - LAG(volume) OVER (PARTITION BY name ORDER BY time))::float / 
                          NULLIF(LAG(volume) OVER (PARTITION BY name ORDER BY time), 0)) * 100
                    ELSE 0 
                END
            ) as growth_percentage
        FROM trends 
        WHERE country_code = $1 
        AND time > NOW() - INTERVAL '24 hours'
        GROUP BY name
        ORDER BY total_volume DESC
        LIMIT $2
        """
        
        try:
            results = await execute_query(query, country_code.upper(), limit, fetch="all")
        except:
            # Se la query fallisce (tabella non esiste, ecc.), usa fallback
            results = []
        
        # Se non ci sono dati specifici per paese, usa trend globali adattati
        if not results or len(results) == 0:
            global_trends = await self.get_global_trends(limit)
            
            # Multiplier per simulare la popolarità nei diversi paesi
            country_multipliers = {
                'US': 1.0,    # USA = baseline
                'GB': 0.35,   # Regno Unito
                'CA': 0.12,   # Canada  
                'AU': 0.08,   # Australia
                'IT': 0.20,   # Italia
                'FR': 0.25,   # Francia
                'DE': 0.28,   # Germania
                'ES': 0.18,   # Spagna
                'NL': 0.06,   # Olanda
                'SE': 0.04,   # Svezia
                'BR': 0.15,   # Brasile
                'MX': 0.10,   # Messico
                'JP': 0.30,   # Giappone
                'KR': 0.15,   # Corea del Sud
                'IN': 0.45,   # India
                'SG': 0.03,   # Singapore
            }
            
            multiplier = country_multipliers.get(country_code.upper(), 0.05)  # Default per paesi non listati
            
            # Adatta i trend globali al paese
            adapted_trends = []
            for trend in global_trends:
                adapted_trend = {
                    "rank": trend["rank"],
                    "name": trend["name"],
                    "volume": int(trend["volume"] * multiplier),
                    "growth_percentage": trend["growth_percentage"],
                    "platforms": trend["platforms"]
                }
                adapted_trends.append(adapted_trend)
            
            return adapted_trends
        
        # Altrimenti usa i dati specifici dal database
        trends = []
        for idx, row in enumerate(results):
            trends.append({
                "rank": idx + 1,
                "name": row['name'],
                "volume": row['total_volume'],
                "growth_percentage": round(row['growth_percentage'] or 0.0, 1),
                "platforms": row['platforms']
            })
        
        return trends
    
    async def analyze_keyword(self, keyword: str, hours_back: int = 24) -> Dict[str, Any]:
        """Analizza le menzioni di una keyword"""
        
        since_time = datetime.now() - timedelta(hours=hours_back)
        
        # Conta menzioni totali per piattaforma
        platform_query = """
        SELECT 
            platform,
            SUM(volume) as total_mentions,
            AVG(sentiment) as avg_sentiment
        FROM mentions 
        WHERE keyword ILIKE $1 
        AND time > $2
        GROUP BY platform
        """
        
        platform_results = await execute_query(platform_query, f"%{keyword}%", since_time)
        
        # Timeline oraria
        timeline_query = """
        SELECT 
            date_trunc('hour', time) as hour,
            SUM(volume) as volume
        FROM mentions 
        WHERE keyword ILIKE $1 
        AND time > $2
        GROUP BY hour
        ORDER BY hour
        """
        
        timeline_results = await execute_query(timeline_query, f"%{keyword}%", since_time)
        
        # Formatta risultati
        platforms = {}
        total_mentions = 0
        sentiment_sum = 0
        sentiment_count = 0
        
        for row in platform_results:
            platforms[row['platform']] = row['total_mentions']
            total_mentions += row['total_mentions']
            if row['avg_sentiment']:
                sentiment_sum += row['avg_sentiment']
                sentiment_count += 1
        
        timeline = [
            {
                "timestamp": int(row['hour'].timestamp()),
                "volume": row['volume']
            }
            for row in timeline_results
        ]
        
        return {
            "keyword": keyword,
            "total_mentions": total_mentions,
            "platforms": platforms,
            "sentiment_avg": round(sentiment_sum / sentiment_count, 2) if sentiment_count > 0 else 0.5,
            "timeline": timeline,
            "analysis_period_hours": hours_back
        }
    
    async def get_related_hashtags(self, hashtag: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Trova hashtag correlati"""
        
        query = """
        SELECT 
            related_hashtag,
            AVG(volume) as avg_volume,
            COUNT(*) as co_occurrences,
            AVG(volume) / (SELECT AVG(volume) FROM hashtag_relations WHERE main_hashtag = $1) as relation_score
        FROM hashtag_relations 
        WHERE main_hashtag = $1
        GROUP BY related_hashtag
        ORDER BY relation_score DESC, avg_volume DESC
        LIMIT $2
        """
        
        results = await execute_query(query, hashtag.lstrip('#'), limit)
        
        related = []
        for row in results:
            related.append({
                "hashtag": f"#{row['related_hashtag']}",
                "relation_score": round(row['relation_score'] or 0.0, 2),
                "volume": int(row['avg_volume'] or 0)
            })
        
        return related
