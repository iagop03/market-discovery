from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Opportunity(Base):
    """A discovered niche, persisted for consumers (e.g. market-orchestrator) to pick up."""

    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(primary_key=True)
    niche_title: Mapped[str] = mapped_column(String(255))
    niche_description: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50), default="other")
    status: Mapped[str] = mapped_column(String(20), default="discovered")
    exported: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "niche_title": self.niche_title,
            "niche_description": self.niche_description,
            "source": self.source,
            "category": self.category,
            "status": self.status,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Niche:
    """In-flight candidate extracted from a post, before it is persisted as an Opportunity."""

    title: str
    description: str
    source: str
    category: str = "other"
    confidence: float = 0.5
