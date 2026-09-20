import asyncio
import time


class RateLimiter:
    """Enforces a minimum interval between successive acquire() calls.

    Distinct from retry.retry_async: retry reacts to a failure that already happened;
    this prevents bursts that would trigger a rate limit in the first place. Each
    scraper owns one instance, sized to that API's published rate limit, and calls
    `await acquire()` once per outbound request.
    """

    def __init__(self, min_interval: float):
        self.min_interval = min_interval
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            wait = self.min_interval - (now - self._last_call)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_call = time.monotonic()
