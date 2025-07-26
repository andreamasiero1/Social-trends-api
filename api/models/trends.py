from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class TrendItem(BaseModel):
    rank: int
    name: str
    volume: int
    growth_percentage: float = 0.0
    platforms: List[str]

class TrendResponse(BaseModel):
    last_updated: datetime
    total_trends: int
    trends: List[TrendItem]

class PlatformTrendItem(BaseModel):
    rank: int
    name: str
    volume: int
    metadata: Dict[str, Any] = {}

class PlatformTrendResponse(BaseModel):
    platform: str
    last_updated: datetime
    total_trends: int
    trends: List[PlatformTrendItem]

class CountryTrendResponse(BaseModel):
    country: str
    last_updated: datetime
    trends: List[TrendItem]

class KeywordAnalysis(BaseModel):
    keyword: str
    total_mentions: int
    platforms: Dict[str, int]
    sentiment_avg: float
    timeline: List[Dict[str, Any]]

class RelatedHashtag(BaseModel):
    hashtag: str
    relation_score: float
    volume: int

class RelatedHashtagsResponse(BaseModel):
    hashtag: str
    related_hashtags: List[RelatedHashtag]
    last_updated: datetime

class ApiKeyInfo(BaseModel):
    key: str
    tier: str
    monthly_limit: int
    current_usage: int
