import asyncio
import logging
from datetime import datetime, timezone

import praw

from market_discovery.retry import retry_async

from .base import Post, SourceScraper

logger = logging.getLogger(__name__)

SUBREDDITS = [
    "webdev", "learnprogramming", "devops", "rust", "golang",
    "Python", "reactjs", "node", "kubernetes", "microservices",
    "AskProgramming", "startups", "business",
]


class RedditScraper(SourceScraper):
    def __init__(self, client_id: str, client_secret: str):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="MarketDiscovery/1.0",
        )

    async def fetch_recent(self, limit: int = 20) -> list[Post]:
        posts: list[Post] = []
        for subreddit_name in SUBREDDITS:
            try:
                posts.extend(await retry_async(lambda: asyncio.to_thread(self._scrape, subreddit_name, limit)))
            except Exception:
                logger.exception("Error scraping r/%s", subreddit_name)
        return posts

    def _scrape(self, subreddit_name: str, limit: int) -> list[Post]:
        posts: list[Post] = []
        subreddit = self.reddit.subreddit(subreddit_name)
        for submission in subreddit.new(limit=limit):
            if submission.score < 5:
                continue
            posts.append(Post(
                text=f"{submission.title}\n{submission.selftext}",
                source="reddit",
                author=submission.author.name if submission.author else "deleted",
                url=f"https://reddit.com{submission.permalink}",
                timestamp=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                upvotes=submission.score,
            ))
        return posts
