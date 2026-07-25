"""Redis-backed fixed-window rate limiting. See
docs/architecture/04-security-and-compliance.md §4: edge (Cloudflare) rate limiting handles
volumetric abuse before it reaches us; this is the application-layer control that protects
individual endpoints from targeted abuse (credential stuffing on /auth/login, registration spam
on /auth/register) regardless of where the traffic originates.

A fixed window (INCR + EXPIRE) is used rather than a true token bucket: it's simpler to reason
about and implement correctly with a single round trip, and the burst-at-window-boundary
imprecision it has (up to ~2x the nominal rate right at a window edge) doesn't matter for the
abuse patterns this defends against. A token bucket is worth the extra complexity for the
per-business/per-API-key limits on the general API surface (Phase 2, once those endpoints exist),
not for these two pre-auth endpoints.
"""

from redis.asyncio import Redis

from app.errors import RateLimitedError

_redis: Redis | None = None


def init_redis(redis_url: str) -> Redis:
    global _redis
    _redis = Redis.from_url(redis_url, decode_responses=True)
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
    _redis = None


def get_redis() -> Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialized — call init_redis() at service startup.")
    return _redis


async def enforce_rate_limit(key: str, *, limit: int, window_seconds: int) -> None:
    """Raises RateLimitedError if `key` has exceeded `limit` requests in the current window."""
    redis = get_redis()
    bucket_key = f"ratelimit:{key}:{window_seconds}"
    current = await redis.incr(bucket_key)
    if current == 1:
        await redis.expire(bucket_key, window_seconds)
    if current > limit:
        raise RateLimitedError(f"Too many requests — limit is {limit} per {window_seconds}s")
