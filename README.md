# market-discovery

Continuous scraper that mines public sources (Reddit, GitHub issues, Hacker News, Stack Overflow) for signals of unmet product demand — "I need X but it doesn't exist", "alternative to Y" — and stores them as candidate `Opportunity` rows.

This is the first stage of a larger pipeline: `market-discovery` finds niches, `market-orchestrator` validates and builds the viable ones with `antcrew`.

## Why a separate repo

`market-discovery` has no dependency on validation or build tooling — it scrapes, extracts, categorizes, and stores. It runs continuously and can be scaled or reused independently of how (or whether) anything downstream acts on its output.

## Setup

```bash
pip install -e ".[dev]"
cp .env.example .env  # fill in Reddit/GitHub credentials
python scripts/init_db.py
```

## Run

```bash
market-discovery
```

Runs a scrape → extract → categorize → store cycle every 12 hours. Set `WEBHOOK_URL` in `.env` to push newly discovered opportunities out as they're stored.

## Expose opportunities over HTTP (optional)

```bash
pip install -e ".[api]"
uvicorn market_discovery.api.app:app --reload
```

`GET /opportunities/new` returns and marks-as-exported any opportunity not yet claimed — this is what `market-orchestrator`'s `DiscoveryClient` polls.

## Tests

```bash
pytest
```
