import asyncio
import logging
from datetime import datetime, timezone

import aiohttp

from market_discovery.retry import retry_async

from .base import Post, SourceScraper

logger = logging.getLogger(__name__)

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"
QUERIES = ["need a tool for", "alternative to", "is broken"]


class HackerNewsScraper(SourceScraper):
    async def fetch_recent(self, limit: int = 20) -> list[Post]:
        posts: list[Post] = []
        async with aiohttp.ClientSession() as session:
            for query in QUERIES:
                try:
                    data = await retry_async(
                        lambda: self._fetch_query(session, query, limit),
                        retry_on=(aiohttp.ClientError, asyncio.TimeoutError),
                    )
                except Exception:
                    logger.exception("Error querying Hacker News for %r", query)
                    continue

                for hit in data.get("hits", []):
                    text = hit.get("comment_text") or hit.get("story_title") or ""
                    if not text:
                        continue
                    posts.append(Post(
                        text=text,
                        source="hackernews",
                        author=hit.get("author", "unknown"),
                        url=f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                        timestamp=datetime.fromtimestamp(hit.get("created_at_i", 0), tz=timezone.utc),
                        upvotes=hit.get("points") or 0,
                    ))
        return posts

    async def _fetch_query(self, session: aiohttp.ClientSession, query: str, limit: int) -> dict:
        params = {"query": query, "tags": "comment", "hitsPerPage": limit}
        async with session.get(
            HN_SEARCH_URL, params=params, timeout=aiohttp.ClientTimeout(total=15)
        ) as resp:
            resp.raise_for_status()
            return await resp.json()
