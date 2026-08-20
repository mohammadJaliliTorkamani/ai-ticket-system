import asyncio
import time
from collections import defaultdict, deque

from fastapi import HTTPException, status

from app.config import get_settings

_buckets: dict[str, deque[float]] = defaultdict(deque)
_lock = asyncio.Lock()


async def enforce_rate_limit(client_key: str) -> int:
    limit = get_settings().requests_per_hour
    cutoff = time.monotonic() - 3600
    async with _lock:
        bucket = _buckets[client_key]
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Hourly request limit reached")
        bucket.append(time.monotonic())
        return limit - len(bucket)
