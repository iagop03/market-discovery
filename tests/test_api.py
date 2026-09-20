from datetime import datetime, timedelta, timezone

from market_discovery.api.app import AckRequest, ack_opportunities, get_new_opportunities, list_opportunities
from market_discovery.models import Opportunity


def test_get_new_opportunities_claims_rows_without_exporting_them(db_session):
    db_session.add(Opportunity(niche_title="A", source="reddit", category="backend", confidence=0.9))
    db_session.add(Opportunity(niche_title="B", source="github", category="devops", confidence=0.6))
    db_session.commit()

    result = get_new_opportunities(limit=50)
    assert {r["niche_title"] for r in result} == {"A", "B"}

    # claimed but not yet acked: must not be handed out again within the visibility window
    assert get_new_opportunities(limit=50) == []

    stored = db_session.query(Opportunity).all()
    assert all(o.claimed_at is not None for o in stored)
    assert all(not o.exported for o in stored)


def test_get_new_opportunities_respects_limit(db_session):
    for i in range(3):
        db_session.add(Opportunity(niche_title=f"niche-{i}", source="reddit"))
    db_session.commit()

    result = get_new_opportunities(limit=2)
    assert len(result) == 2


def test_ack_opportunities_marks_them_exported(db_session):
    db_session.add(Opportunity(niche_title="A", source="reddit"))
    db_session.commit()

    [claimed] = get_new_opportunities(limit=50)
    response = ack_opportunities(AckRequest(ids=[claimed["id"]]))

    assert response == {"acked": 1}
    stored = db_session.query(Opportunity).filter_by(id=claimed["id"]).one()
    assert stored.exported is True


def test_unacked_claim_becomes_visible_again_after_timeout(db_session):
    db_session.add(Opportunity(niche_title="Stale claim", source="reddit"))
    db_session.commit()

    get_new_opportunities(limit=50)  # claims it

    # simulate a crashed consumer: the claim is older than the visibility timeout
    stored = db_session.query(Opportunity).filter_by(niche_title="Stale claim").one()
    stored.claimed_at = datetime.now(timezone.utc) - timedelta(minutes=30)
    db_session.commit()

    result = get_new_opportunities(limit=50)
    assert [r["niche_title"] for r in result] == ["Stale claim"]


def test_list_opportunities_filters_by_category_and_confidence(db_session):
    db_session.add(Opportunity(niche_title="Backend thing", source="reddit", category="backend", confidence=0.9))
    db_session.add(Opportunity(niche_title="Frontend thing", source="reddit", category="frontend", confidence=0.9))
    db_session.add(Opportunity(niche_title="Low confidence", source="reddit", category="backend", confidence=0.1))
    db_session.commit()

    backend_only = list_opportunities(category="backend", min_confidence=0.0)
    assert {r["niche_title"] for r in backend_only} == {"Backend thing", "Low confidence"}

    high_confidence = list_opportunities(category=None, min_confidence=0.5)
    assert {r["niche_title"] for r in high_confidence} == {"Backend thing", "Frontend thing"}
