"""Slack Incoming Webhook integration adapter."""

import logging
import uuid
import httpx

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas.posting import PlatformPostingResult

logger = logging.getLogger(__name__)


class SlackPlatform(BasePlatform):
    """Publishes messages via Slack Incoming Webhook API."""

    def __init__(self, webhook_url: str = None):
        super().__init__(name="Slack", is_public=False)
        self.webhook_url = webhook_url or settings.SLACK_WEBHOOK_URL

    async def post_message(self, message: str) -> PlatformPostingResult:
        """Publishes message to Slack channel."""
        if not self.webhook_url:
            if settings.MOCK_POSTING:
                fake_ts = f"p{uuid.uuid4().int % 1000000000000000}"
                posted_url = f"https://workspace.slack.com/archives/C01234567/{fake_ts}"
                logger.info("[MOCK] Slack post succeeded: %s", posted_url)
                return self._build_success_result(posted_url)
            return self._build_failure_result("Authentication failed: Missing SLACK_WEBHOOK_URL.")

        try:
            payload = {"text": message}
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook_url, json=payload)
                resp.raise_for_status()
                # Slack returns 200 with text 'ok'
                if resp.text.strip().lower() != "ok":
                    return self._build_failure_result(f"Slack webhook rejected payload: {resp.text}")

                posted_url = "https://slack.com/app_redirect?channel=general"
                return self._build_success_result(posted_url)
        except httpx.HTTPStatusError as e:
            return self._build_failure_result(f"Slack API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            return self._build_failure_result(f"Slack connection error: {str(e)}")
