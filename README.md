# market-discovery

Continuous scraper that mines public sources (Reddit, GitHub issues, Hacker News, Stack Overflow) for signals of unmet product demand — "I need X but it doesn't exist", "alternative to Y" — and stores them as candidate `Opportunity` rows.

This is the first stage of a larger pipeline: `market-discovery` finds niches, `market-orchestrator` validates and builds the viable ones with `antcrew`.

## Why a separate repo

`market-discovery` has no dependency on validation or build tooling — it scrapes, extracts, categorizes, and stores. It runs continuously and can be scaled or reused independently of how (or whether) anything downstream acts on its output.

## Setup

```bash
pip install -e ".[dev]"
cp .env.example .env  # fill in Reddit/GitHub credentials
python scripts/init_db.py  # applies Alembic migrations
```

## Database migrations

Schema changes go through Alembic (`alembic/versions/`), not `Base.metadata.create_all()` directly —
`create_all()` only creates missing tables, so an existing deployed DB would silently miss any new
column added to a model. After changing a model:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

`scripts/init_db.py` (`alembic upgrade head`) is the one command to run on a fresh or an existing DB.

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

`GET /opportunities/new` claims any opportunity not yet claimed and returns it — this is what `market-orchestrator`'s `DiscoveryClient` polls. A claim is provisional: it must be confirmed with `POST /opportunities/ack {"ids": [...]}` once the caller has durably stored it, otherwise the claim expires after 10 minutes and the opportunity becomes claimable again. This makes delivery at-least-once (safe here since the orchestrator dedupes by niche title + source) instead of at-most-once, so a crash between claim and ack never silently drops an opportunity.

## Tests

```bash
pytest
```

## Running the full pipeline locally

See `docker-compose.yml` in `market-orchestrator` (assumes both repos are checked out as
siblings) — it builds and runs both services together, each with its own Postgres, for a local
smoke test of discovery → validate → build end to end.
