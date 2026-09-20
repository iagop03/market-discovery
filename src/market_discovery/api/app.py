from contextlib import asynccontextmanager

from fastapi import FastAPI

from market_discovery.config import Settings
from market_discovery.database import get_session, init_db
from market_discovery.models import Opportunity


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(Settings().database_url)
    yield


app = FastAPI(title="market-discovery", lifespan=lifespan)


@app.get("/opportunities/new")
def get_new_opportunities(limit: int = 50):
    """Returns not-yet-synced opportunities and marks them exported.

    Consumed by market-orchestrator's DiscoveryClient — each opportunity is
    returned to exactly one caller, so orchestrator never has to de-duplicate.
    """
    session = get_session()
    try:
        opportunities = (
            session.query(Opportunity)
            .filter_by(exported=False)
            .limit(limit)
            .all()
        )
        result = [opp.to_dict() for opp in opportunities]
        for opp in opportunities:
            opp.exported = True
        session.commit()
        return result
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
