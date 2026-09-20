import asyncio
import logging
from datetime import timezone

from github import Github

from .base import Post, SourceScraper

logger = logging.getLogger(__name__)

SEARCH_QUERIES = [
    '"is there a tool for" in:body is:issue',
    '"looking for an alternative to" in:body is:issue',
    '"we need a" in:body is:issue',
]


class GitHubScraper(SourceScraper):
    def __init__(self, token: str = ""):
        if not token:
            logger.warning(
                "GitHubScraper running unauthenticated — GitHub's search API "
                "rate-limits unauthenticated requests heavily; set GITHUB_TOKEN."
            )
        self.github = Github(token) if token else Github()

    async def fetch_recent(self, limit: int = 20) -> list[Post]:
        posts: list[Post] = []
        for query in SEARCH_QUERIES:
            try:
                posts.extend(await asyncio.to_thread(self._search, query, limit))
            except Exception:
                logger.exception("Error searching GitHub issues for %r", query)
        return posts

    def _search(self, query: str, limit: int) -> list[Post]:
        posts: list[Post] = []
        issues = self.github.search_issues(query=query, sort="created", order="desc")
        for issue in issues[:limit]:
            timestamp = issue.created_at
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            posts.append(Post(
                text=f"{issue.title}\n{issue.body or ''}",
                source="github",
                author=issue.user.login if issue.user else "unknown",
                url=issue.html_url,
                timestamp=timestamp,
                upvotes=issue.comments,
            ))
        return posts
