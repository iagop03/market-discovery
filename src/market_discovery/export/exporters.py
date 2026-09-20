import logging

import aiohttp

logger = logging.getLogger(__name__)


class WebhookExporter:
    """Pushes newly discovered opportunities to a configured webhook (e.g. market-orchestrator or Slack)."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send_batch(self, opportunities) -> None:
        payload = {"opportunities": [opp.to_dict() for opp in opportunities]}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url, json=payload, timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    resp.raise_for_status()
        except Exception:
            logger.exception("Failed to export %d opportunities to webhook", len(opportunities))
