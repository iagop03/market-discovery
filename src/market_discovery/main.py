import asyncio
import logging

from market_discovery.config import Settings
from market_discovery.database import get_session, init_db
from market_discovery.export import WebhookExporter
from market_discovery.extractors import Categorizer, PatternExtractor
from market_discovery.models import Opportunity
from market_discovery.sources import GitHubScraper, HackerNewsScraper, RedditScraper, StackOverflowScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

CYCLE_INTERVAL_SECONDS = 12 * 3600


class DiscoveryOrchestrator:
    """Main loop: scrape -> extract -> categorize -> store -> export."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.sources = [
            RedditScraper(settings.reddit_client_id, settings.reddit_client_secret),
            GitHubScraper(settings.github_token),
            StackOverflowScraper(),
            HackerNewsScraper(),
        ]
        self.extractor = PatternExtractor()
        self.categorizer = Categorizer()
        self.exporter = WebhookExporter(settings.webhook_url) if settings.webhook_url else None

    async def run(self) -> None:
        while True:
            try:
                await self.discovery_cycle()
                logger.info("Discovery cycle complete")
            except Exception:
                logger.exception("Discovery cycle failed")
            await asyncio.sleep(CYCLE_INTERVAL_SECONDS)

    async def discovery_cycle(self) -> None:
        logger.info("Starting discovery cycle...")

        all_posts = []
        for source in self.sources:
            logger.info("Scraping %s...", type(source).__name__)
            posts = await source.fetch_recent()
            all_posts.extend(posts)
            logger.info("  found %d posts", len(posts))

        if not all_posts:
            logger.warning("No posts found in any source")
            return

        niches = []
        for post in all_posts:
            niches.extend(self.extractor.extract(post.text, post.source))
        logger.info("Extracted %d potential niches", len(niches))

        niches = [self.categorizer.categorize(niche) for niche in niches]
        niches = self._deduplicate(niches)
        logger.info("%d unique niches after dedup", len(niches))

        session = get_session()
        try:
            new_opportunities = []
            for niche in niches:
                opp = self._save_opportunity(session, niche)
                if opp is not None:
                    new_opportunities.append(opp)
            session.commit()
            logger.info("Stored %d new opportunities", len(new_opportunities))

            if self.exporter and new_opportunities:
                await self.exporter.send_batch(new_opportunities)
        finally:
            session.close()

    def _deduplicate(self, niches):
        unique = {}
        for niche in niches:
            key = niche.title.lower().strip()
            unique.setdefault(key, niche)
        return list(unique.values())

    def _save_opportunity(self, session, niche):
        existing = (
            session.query(Opportunity)
            .filter_by(niche_title=niche.title, source=niche.source)
            .first()
        )
        if existing:
            return None

        opp = Opportunity(
            niche_title=niche.title,
            niche_description=niche.description,
            source=niche.source,
            category=niche.category,
            confidence=niche.confidence,
            status="discovered",
        )
        session.add(opp)
        return opp


async def _main() -> None:
    settings = Settings()
    init_db(settings.database_url)
    await DiscoveryOrchestrator(settings).run()


def cli() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    cli()
