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


def test_does_not_span_lines_on_multiline_body():
    """Regression guard: [^.!?] matches newlines too, so on a long, mostly-unpunctuated
    multi-line body (typical of a GitHub issue) a naive pattern used to capture clear
    across paragraphs instead of stopping at the end of the current line."""
    extractor = PatternExtractor()
    text = (
        "Steps to reproduce\n"
        "- clone the repo\n"
        "- run the build script\n"
        "- observe the output\n"
        "\n"
        "The CI pipeline is broken on main.\n"
        "Unrelated trailing notes about something else entirely that go on for a while"
    )
    niches = extractor.extract(text, source="github")
    titles = [n.title for n in niches]
    assert any(t == "the ci pipeline" for t in titles)
    assert not any("\n" in t for t in titles)
    assert not any("unrelated trailing notes" in t for t in titles)
