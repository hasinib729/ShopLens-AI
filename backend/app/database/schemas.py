from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Auth Schemas
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    email: str

class TokenData(BaseModel):
    email: Optional[str] = None

class PasswordReset(BaseModel):
    email: str
    new_password: str

# Product Schemas
class ProductBase(BaseModel):
    product_id: str
    title: str
    description: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    rating: float = 0.0
    reviews_count: int = 0
    features: Optional[Dict[str, Any]] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Query Understanding Schemas
class QueryUnderstandingResult(BaseModel):
    query: str
    category: Optional[str] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    max_price: Optional[float] = None

# Search Schemas
class TextSearchRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    use_ranker: Optional[bool] = True
    experiment_name: Optional[str] = None

class HybridSearchRequest(BaseModel):
    query: str
    image_filename: str  # Uploaded image filename
    session_id: Optional[str] = None
    use_ranker: Optional[bool] = True

class SearchResultCard(BaseModel):
    product: ProductResponse
    relevance_score: float  # Visual or Semantic similarity
    final_rank_score: float  # Multi-factor score
    feature_contributions: Dict[str, float]  # For explainable rank display

class SearchResponse(BaseModel):
    results: List[SearchResultCard]
    query_understanding: QueryUnderstandingResult
    latency_ms: float
    total_found: int

# Recommendation Schemas
class RecommendationRequest(BaseModel):
    user_id: Optional[int] = None
    session_id: str
    limit: Optional[int] = 10

class RecommendationCard(BaseModel):
    product: ProductResponse
    score: float
    explanation: str  # e.g., "Recommended because you viewed running shoes" or "94% visual similarity"

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationCard]
    latency_ms: float

# Analytics & Dashboard Schemas
class KPISummary(BaseModel):
    total_products: int
    total_searches: int
    total_recommendations: int
    active_users: int
    search_success_rate: float
    recommendation_ctr: float

class DatasetStats(BaseModel):
    total_products: int = 2100000
    total_images: int = 1800000
    total_categories: int = 420
    total_queries: int = 1300000
    total_interactions: int = 5600000

class FunnelStage(BaseModel):
    stage: str
    count: int
    rate: float

class FunnelSummary(BaseModel):
    stages: List[FunnelStage]
    ctr: float
    add_to_cart_rate: float
    conversion_rate: float
    revenue_attribution: float

class ModelMetricsDetail(BaseModel):
    recall_at_10: float
    precision_at_10: float
    ndcg_at_10: float
    mrr: float
    map: float
    hit_rate: float

class DriftMetrics(BaseModel):
    embedding_drift: float
    feature_drift: float
    latency_drift: float
    alerts: List[str]

# A/B Experiment Schemas
class ABExperimentCreate(BaseModel):
    experiment_name: str
    model_a_name: str
    model_b_name: str

class ABExperimentResponse(BaseModel):
    id: int
    experiment_name: str
    model_a_name: str
    model_b_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ABExperimentLogRequest(BaseModel):
    experiment_name: str
    session_id: str
    group_name: str
    product_id: int
    action: str  # "click" or "purchase"
