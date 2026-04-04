"""
Redis client — added in Phase 3.
Used for availability locks during checkout and short-lived caches.

Required environment variables (Phase 3):
  REDIS_URL — full Redis connection string, e.g.:
    redis://default:password@host:6379
"""
import os
import redis

_client = None


def get_client():
    """Return a shared Redis client, creating it on first call."""
    global _client
    if _client is None:
        url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        _client = redis.from_url(url, decode_responses=True)
    return _client
