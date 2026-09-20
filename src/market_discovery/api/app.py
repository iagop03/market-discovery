from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import or_

from market_discovery.config import Settings
from market_discovery.database import get_session, init_db
from market_discovery.models import Opportunity

# How long a claimed-but-unacked opportunity stays hidden from other callers before
# it becomes claimable again. Bounds the at-most-once window from below: a crash
# between claim and ack costs at most this much delay, not the opportunity itself.
CLAIM_VISIBILITY_TIMEOUT = timedelta(minutes=10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(Settings().database_url)
    yield


app = FastAPI(title="market-discovery", lifespan=lifespan)


class AckRequest(BaseModel):
    ids: list[int]


@app.get("/opportunities/new")
def get_new_opportunities(limit: int = 50):
    """Claims not-yet-acked opportunities for delivery.

    Consumed by market-orchestrator's DiscoveryClient. A claimed opportunity is
    hidden from further claims for CLAIM_VISIBILITY_TIMEOUT but is NOT yet
    retired — the caller must confirm durable receipt via POST /opportunities/ack,
    otherwise the claim expires and the opportunity becomes claimable again.
    This makes delivery at-least-once rather than at-most-once: safe because
    the orchestrator dedupes by niche_title+source, so redelivery after a
    crash never produces a duplicate.
    """
    session = get_session()
    try:
        cutoff = datetime.now(timezone.utc) - CLAIM_VISIBILITY_TIMEOUT
        opportunities = (
            session.query(Opportunity)
            .filter_by(exported=False)
            .filter(or_(Opportunity.claimed_at.is_(None), Opportunity.claimed_at < cutoff))
            .order_by(Opportunity.created_at)
            .limit(limit)
            .all()
        )
        result = [opp.to_dict() for opp in opportunities]
        for opp in opportunities:
            opp.claimed_at = datetime.now(timezone.utc)
        session.commit()
        return result
    finally:
        session.close()


@app.post("/opportunities/ack")
def ack_opportunities(body: AckRequest):
    """Confirms an opportunity was durably stored downstream; only then is it retired for good."""
    session = get_session()
    try:
        updated = (
            session.query(Opportunity)
            .filter(Opportunity.id.in_(body.ids))
            .update({"exported": True}, synchronize_session=False)
        )
        session.commit()
        return {"acked": updated}
    finally:
        session.close()


@app.get("/opportunities")
def list_opportunities(category: str | None = None, min_confidence: float = 0.0):
    session = get_session()
    try:
        query = session.query(Opportunity).filter(Opportunity.confidence >= min_confidence)
        if category:
            query = query.filter_by(category=category)
        return [opp.to_dict() for opp in query.all()]
    finally:
        session.close()
