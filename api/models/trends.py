from pydantic import BaseModel, Field, EmailStr
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

# Nuovi modelli per il sistema utenti migliorato

class UserRegistrationRequest(BaseModel):
    email: EmailStr
    tier: str = Field(default="free", pattern="^(free|developer|business|enterprise)$")

class UserRegistrationResponse(BaseModel):
    message: str
    api_key: Optional[str] = None
    requires_email_verification: bool = False
    verification_sent_to: Optional[str] = None

class RapidAPIKeyRequest(BaseModel):
    email: EmailStr
    tier: str
    rapidapi_user_id: str

class RapidAPIKeyResponse(BaseModel):
    api_key: str
    user_id: int
    tier: str
    monthly_limit: int

class EmailVerificationRequest(BaseModel):
    token: str

class EmailVerificationResponse(BaseModel):
    message: str
    api_key: Optional[str] = None

class UserInfo(BaseModel):
    id: int
    email: str
    is_email_verified: bool
    registration_source: str
    created_at: datetime

class ApiKeyDetailed(BaseModel):
    id: int
    key: str
    tier: str
    monthly_limit: int
    usage_count: int
    source: str
    is_active: bool
    created_at: datetime
    last_used: Optional[datetime]
