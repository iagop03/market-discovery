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


def test_categorizes_mobile_keyword():
    niche = Niche(title="a flutter app for tracking workouts", description="", source="reddit")
    result = Categorizer().categorize(niche)
    assert result.category == "mobile"


def test_react_native_categorizes_as_mobile_not_frontend():
    """Regression guard: "react native" contains "react", frontend's own keyword —
    mobile must be checked first or this always miscategorizes as frontend."""
    niche = Niche(title="React Native inventory tracker for warehouses", description="", source="reddit")
    result = Categorizer().categorize(niche)
    assert result.category == "mobile"
