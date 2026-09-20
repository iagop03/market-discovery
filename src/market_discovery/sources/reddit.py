import logging
from datetime import datetime, timezone

import praw

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
            except Exception:
                logger.exception("Error scraping r/%s", subreddit_name)
        return posts
