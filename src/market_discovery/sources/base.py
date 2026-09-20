from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Post:
    text: str
    source: str
    author: str
    url: str
    timestamp: datetime
    upvotes: int = 0


class SourceScraper(ABC):
    """Common interface every source implements. Discovery only ever calls fetch_recent()."""

    @abstractmethod
    async def fetch_recent(self, limit: int = 100) -> list[Post]:
        ...
