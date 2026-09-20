import pytest

from market_discovery.retry import retry_async


async def test_retry_async_returns_result_on_first_success():
    async def op():
        return "ok"

    assert await retry_async(op, attempts=3, base_delay=0) == "ok"


async def test_retry_async_retries_then_succeeds(monkeypatch):
    monkeypatch.setattr("market_discovery.retry.asyncio.sleep", _instant_sleep)
    calls = {"n": 0}

    async def op():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("transient")
        return "ok"

    result = await retry_async(op, attempts=3, base_delay=0.01)

    assert result == "ok"
    assert calls["n"] == 3


async def test_retry_async_raises_last_exception_after_exhausting_attempts(monkeypatch):
    monkeypatch.setattr("market_discovery.retry.asyncio.sleep", _instant_sleep)
    calls = {"n": 0}

    async def op():
        calls["n"] += 1
        raise ValueError(f"failure {calls['n']}")

    with pytest.raises(ValueError, match="failure 2"):
        await retry_async(op, attempts=2, base_delay=0.01)

    assert calls["n"] == 2


async def test_retry_async_only_retries_configured_exception_types():
    async def op():
        raise KeyError("not retried")

    with pytest.raises(KeyError):
        await retry_async(op, attempts=3, base_delay=0, retry_on=(ValueError,))


async def _instant_sleep(_seconds):
    return None
