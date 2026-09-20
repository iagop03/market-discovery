"""One-off script: create tables for the configured DATABASE_URL."""

from market_discovery.config import Settings
from market_discovery.database import init_db

if __name__ == "__main__":
    settings = Settings()
    init_db(settings.database_url)
    print(f"Initialized schema at {settings.database_url}")
