import asyncio

from market_discovery.rate_limit import RateLimiter


async def test_first_acquire_does_not_wait():
    limiter = RateLimiter(min_interval=10.0)
    start = asyncio.get_event_loop().time()
    await limiter.acquire()
    assert asyncio.get_event_loop().time() - start < 0.05


async def test_second_acquire_waits_out_the_remaining_interval(monkeypatch):
    slept = []

    async def fake_sleep(seconds):
        slept.append(seconds)

    monkeypatch.setattr("market_discovery.rate_limit.asyncio.sleep", fake_sleep)

    limiter = RateLimiter(min_interval=5.0)
    await limiter.acquire()
    await limiter.acquire()

    assert len(slept) == 1
    assert 0 < slept[0] <= 5.0


async def test_acquire_does_not_wait_once_enough_time_has_passed(monkeypatch):
    limiter = RateLimiter(min_interval=0.05)
    await limiter.acquire()
    await asyncio.sleep(0.1)

    start = asyncio.get_event_loop().time()
    await limiter.acquire()
    assert asyncio.get_event_loop().time() - start < 0.05
