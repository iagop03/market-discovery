import asyncio
import logging
from datetime import datetime, timezone

import aiohttp

from market_discovery.rate_limit import RateLimiter
from market_discovery.retry import retry_async

from .base import Post, SourceScraper

logger = logging.getLogger(__name__)

SO_SEARCH_URL = "https://api.stackexchange.com/2.3/search/advanced"
TAGS = ["python", "devops", "rest-api", "docker", "kubernetes"]


class StackOverflowScraper(SourceScraper):
    def __init__(self) -> None:
        # Anonymous StackExchange quota is small (300/day); throttling avoids bursting
        # what's left of it in one cycle, even though it can't fix quota exhaustion itself.
        self._rate_limiter = RateLimiter(min_interval=1.0)

    async def fetch_recent(self, limit: int = 20) -> list[Post]:
        posts: list[Post] = []
        async with aiohttp.ClientSession() as session:
            for tag in TAGS:
                await self._rate_limiter.acquire()
                try:
                    data = await retry_async(
                        lambda: self._fetch_tag(session, tag, limit),
                        retry_on=(aiohttp.ClientError, asyncio.TimeoutError),
                    )
                except Exception:
                    logger.exception("Error querying Stack Overflow for tag %r", tag)
                    continue

                for item in data.get("items", []):
                    posts.append(Post(
                        text=f"{item.get('title', '')}\n{item.get('body', '')}",
                        source="stackoverflow",
                        author=item.get("owner", {}).get("display_name", "unknown"),
                        url=item.get("link", ""),
                        timestamp=datetime.fromtimestamp(item.get("creation_date", 0), tz=timezone.utc),
                        upvotes=item.get("score", 0),
                    ))
        return posts

    async def _fetch_tag(self, session: aiohttp.ClientSession, tag: str, limit: int) -> dict:
        params = {
            "order": "desc",
            "sort": "creation",
            "tagged": tag,
            "site": "stackoverflow",
            "pagesize": limit,
            "filter": "withbody",
        }
        async with session.get(
            SO_SEARCH_URL, params=params, timeout=aiohttp.ClientTimeout(total=15)
        ) as resp:
            resp.raise_for_status()
            return await resp.json()
