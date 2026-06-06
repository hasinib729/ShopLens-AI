import json
from typing import Any, Optional
from app.utils.config import settings

# Global client
_redis_client = None
REDIS_AVAILABLE = False

try:
    import redis
    _redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
        socket_timeout=1.0
    )
    _redis_client.ping()
    REDIS_AVAILABLE = True
except Exception:
    pass

class MemoryCache:
    """In-memory dictionary cache fallback when Redis is offline."""
    def __init__(self):
        self._cache = {}
        
    def get(self, key: str) -> Optional[str]:
        return self._cache.get(key)
        
    def set(self, key: str, value: str, ex: Optional[int] = None):
        self._cache[key] = value
        
    def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]

class CacheService:
    def __init__(self):
        if REDIS_AVAILABLE and _redis_client:
            self.client = _redis_client
        else:
            self.client = MemoryCache()
            
    def get(self, key: str) -> Optional[str]:
        try:
            return self.client.get(key)
        except Exception:
            return None
            
    def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        try:
            if isinstance(self.client, MemoryCache):
                self.client.set(key, value, expire_seconds)
            else:
                if expire_seconds:
                    self.client.setex(key, expire_seconds, value)
                else:
                    self.client.set(key, value)
            return True
        except Exception:
            return False
            
    def delete(self, key: str) -> bool:
        try:
            self.client.delete(key)
            return True
        except Exception:
            return False

cache_service = CacheService()
