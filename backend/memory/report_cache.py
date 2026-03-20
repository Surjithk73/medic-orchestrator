import json
from typing import Dict, Any, Optional
from backend.memory.context_manager import context_manager


class ReportCache:
    """
    Caches completed research reports in Redis to avoid re-running
    expensive pipelines for the same molecule.
    
    Cache key: canonical molecule name (e.g., "ASPIRIN", "METFORMIN")
    TTL: 7 days (configurable)
    """
    
    def __init__(self, ttl_days: int = 7):
        self.ttl_seconds = ttl_days * 86400
    
    def _cache_key(self, canonical_name: str) -> str:
        """Generate Redis key for cached report"""
        # Normalize to uppercase for consistency
        return f"report_cache:{canonical_name.upper()}"
    
    async def get(self, canonical_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached report for a molecule.
        Returns None if not cached or expired.
        """
        key = self._cache_key(canonical_name)
        try:
            cached = await context_manager._redis_command("GET", key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    async def set(self, canonical_name: str, report_data: Dict[str, Any]):
        """
        Cache a completed report.
        Includes TTL to auto-expire stale data.
        """
        key = self._cache_key(canonical_name)
        try:
            await context_manager._redis_command(
                "SET", 
                key, 
                json.dumps(report_data), 
                "EX", 
                self.ttl_seconds
            )
            print(f"Cached report for {canonical_name} (TTL: {self.ttl_seconds}s)")
        except Exception as e:
            print(f"Cache set error: {e}")
    
    async def exists(self, canonical_name: str) -> bool:
        """Check if a cached report exists"""
        key = self._cache_key(canonical_name)
        try:
            result = await context_manager._redis_command("EXISTS", key)
            return bool(result)
        except Exception:
            return False
    
    async def invalidate(self, canonical_name: str):
        """Manually invalidate a cached report"""
        key = self._cache_key(canonical_name)
        try:
            await context_manager._redis_command("DEL", key)
            print(f"Invalidated cache for {canonical_name}")
        except Exception as e:
            print(f"Cache invalidate error: {e}")
    
    async def get_ttl(self, canonical_name: str) -> Optional[int]:
        """Get remaining TTL in seconds for a cached report"""
        key = self._cache_key(canonical_name)
        try:
            ttl = await context_manager._redis_command("TTL", key)
            return int(ttl) if ttl and int(ttl) > 0 else None
        except Exception:
            return None


report_cache = ReportCache(ttl_days=7)
