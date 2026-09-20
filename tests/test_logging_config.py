import json
import logging

from market_discovery.logging_config import JsonFormatter


def _format(record: logging.LogRecord) -> dict:
    return json.loads(JsonFormatter().format(record))


def test_formats_basic_fields_as_json():
    record = logging.LogRecord(
        name="market_discovery.sources.reddit",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="scraped %d posts",
        args=(5,),
        exc_info=None,
    )

    payload = _format(record)

    assert payload["level"] == "INFO"
    assert payload["logger"] == "market_discovery.sources.reddit"
    assert payload["message"] == "scraped 5 posts"
    assert "timestamp" in payload
    assert "exception" not in payload


def test_includes_exception_info_when_present():
    try:
        raise ValueError("boom")
    except ValueError:
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="failed",
            args=(),
            exc_info=True,
        )
        import sys
        record.exc_info = sys.exc_info()

    payload = _format(record)

    assert "ValueError: boom" in payload["exception"]


def test_includes_extra_fields():
    record = logging.LogRecord(
        name="test",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg="rate limited",
        args=(),
        exc_info=None,
    )
    record.niche_title = "COBOL translator"

    payload = _format(record)

    assert payload["niche_title"] == "COBOL translator"
