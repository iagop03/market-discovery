from market_discovery.extractors.pattern_extractor import PatternExtractor


def test_extracts_need_but_pattern():
    extractor = PatternExtractor()
    text = "I need a COBOL to Python translator but it doesn't exist anywhere."
    niches = extractor.extract(text, source="reddit")
    assert any("cobol to python translator" in n.title for n in niches)


def test_ignores_short_matches():
    extractor = PatternExtractor()
    niches = extractor.extract("need x but", source="reddit")
    assert niches == []
