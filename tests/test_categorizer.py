from market_discovery.extractors.categorizer import Categorizer
from market_discovery.models import Niche


def test_categorizes_devops_keyword():
    niche = Niche(title="a tool for docker deployments", description="", source="reddit")
    result = Categorizer().categorize(niche)
    assert result.category == "devops"


def test_defaults_to_other():
    niche = Niche(title="something with no matching keyword at all", description="", source="reddit")
    result = Categorizer().categorize(niche)
    assert result.category == "other"
