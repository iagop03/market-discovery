from market_discovery.api.app import get_new_opportunities, list_opportunities
from market_discovery.models import Opportunity


def test_get_new_opportunities_marks_returned_rows_as_exported(db_session):
    db_session.add(Opportunity(niche_title="A", source="reddit", category="backend", confidence=0.9))
    db_session.add(Opportunity(niche_title="B", source="github", category="devops", confidence=0.6))
    db_session.commit()

    result = get_new_opportunities(limit=50)
    assert {r["niche_title"] for r in result} == {"A", "B"}

    # already exported: a second call must not return the same rows again
    assert get_new_opportunities(limit=50) == []

    stored = db_session.query(Opportunity).all()
    assert all(o.exported for o in stored)


def test_get_new_opportunities_respects_limit(db_session):
    for i in range(3):
        db_session.add(Opportunity(niche_title=f"niche-{i}", source="reddit"))
    db_session.commit()

    result = get_new_opportunities(limit=2)
    assert len(result) == 2


def test_list_opportunities_filters_by_category_and_confidence(db_session):
    db_session.add(Opportunity(niche_title="Backend thing", source="reddit", category="backend", confidence=0.9))
    db_session.add(Opportunity(niche_title="Frontend thing", source="reddit", category="frontend", confidence=0.9))
    db_session.add(Opportunity(niche_title="Low confidence", source="reddit", category="backend", confidence=0.1))
    db_session.commit()

    backend_only = list_opportunities(category="backend", min_confidence=0.0)
    assert {r["niche_title"] for r in backend_only} == {"Backend thing", "Low confidence"}

    high_confidence = list_opportunities(category=None, min_confidence=0.5)
    assert {r["niche_title"] for r in high_confidence} == {"Backend thing", "Frontend thing"}
