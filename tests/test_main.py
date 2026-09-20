from market_discovery.config import Settings
from market_discovery.main import DiscoveryOrchestrator
from market_discovery.models import Niche, Opportunity


def make_orchestrator():
    return DiscoveryOrchestrator(Settings())


def test_deduplicate_collapses_case_and_whitespace_variants():
    orchestrator = make_orchestrator()
    niches = [
        Niche(title="COBOL to Python translator", description="a", source="github"),
        Niche(title="  cobol to python translator  ", description="b", source="github"),
        Niche(title="A different niche", description="c", source="reddit"),
    ]

    unique = orchestrator._deduplicate(niches)

    assert len(unique) == 2
    assert unique[0].description == "a"  # first occurrence wins


def test_save_opportunity_skips_existing_title_and_source(db_session):
    orchestrator = make_orchestrator()
    db_session.add(Opportunity(niche_title="Existing niche", source="reddit"))
    db_session.commit()

    niche = Niche(title="Existing niche", description="x", source="reddit")
    result = orchestrator._save_opportunity(db_session, niche)

    assert result is None
    assert db_session.query(Opportunity).filter_by(niche_title="Existing niche").count() == 1


def test_save_opportunity_stores_new_niche(db_session):
    orchestrator = make_orchestrator()
    niche = Niche(title="Brand new niche", description="desc", source="hackernews", category="devops", confidence=0.7)

    result = orchestrator._save_opportunity(db_session, niche)
    db_session.commit()

    assert result is not None
    stored = db_session.query(Opportunity).filter_by(niche_title="Brand new niche").one()
    assert stored.source == "hackernews"
    assert stored.category == "devops"
    assert stored.confidence == 0.7
    assert stored.status == "discovered"
