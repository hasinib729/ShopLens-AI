import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.utils.config import settings
from app.feature_store.offline_store import OfflineFeatureStore

# Try importing Redis client
REDIS_AVAILABLE = False
_redis_client = None

try:
    import redis
    _redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
        socket_timeout=1.0
    )
    # Check connection
    _redis_client.ping()
    REDIS_AVAILABLE = True
except Exception:
    # Redis offline or not installed
    pass

class OnlineFeatureStore:
    @staticmethod
    def get_user_features(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Retrieves user features for real-time recommendations.
        Checks Redis cache first, falls back to Database + Offline Store calculation.
        """
        cache_key = f"features:user:{user_id}"
        
        if REDIS_AVAILABLE and _redis_client:
            try:
                cached_data = _redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                print(f"Redis get user features error: {e}")
                
        # Cache miss or Redis unavailable - query db
        features = OfflineFeatureStore.get_user_features(db, user_id)
        
        # Save to cache if Redis is working
        if REDIS_AVAILABLE and _redis_client and features:
            try:
                _redis_client.setex(cache_key, 3600, json.dumps(features))  # Cache for 1 hour
            except Exception as e:
                print(f"Redis set user features error: {e}")
                
        return features

    @staticmethod
    def get_product_features(db: Session, product_id: int) -> Dict[str, Any]:
        """
        Retrieves product features for real-time LTR ranking.
        Checks Redis cache first, falls back to Database calculation.
        """
        cache_key = f"features:product:{product_id}"
        
        if REDIS_AVAILABLE and _redis_client:
            try:
                cached_data = _redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                print(f"Redis get product features error: {e}")
                
        # Cache miss - query db
        features = OfflineFeatureStore.get_product_features(db, product_id)
        
        # Save to cache
        if REDIS_AVAILABLE and _redis_client and features:
            try:
                _redis_client.setex(cache_key, 3600, json.dumps(features))  # Cache for 1 hour
            except Exception as e:
                print(f"Redis set product features error: {e}")
                
        return features
        
    @staticmethod
    def invalidate_cache(entity_type: str, entity_id: int):
        """Invalidates Redis cache for a user or product when new events occur."""
        if REDIS_AVAILABLE and _redis_client:
            try:
                cache_key = f"features:{entity_type}:{entity_id}"
                _redis_client.delete(cache_key)
            except Exception as e:
                print(f"Redis delete cache error: {e}")
                
# Global online feature store instance
online_store = OnlineFeatureStore()
