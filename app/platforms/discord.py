"""Discord Webhook integration adapter."""

import logging
import uuid
import httpx

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas.posting import PlatformPostingResult

logger = logging.getLogger(__name__)


class DiscordPlatform(BasePlatform):
    """Publishes messages via Discord Webhooks API."""

    def __init__(self, webhook_url: str = None):
        super().__init__(name="Discord", is_public=False)
        self.webhook_url = webhook_url or settings.DISCORD_WEBHOOK_URL

    async def post_message(self, message: str) -> PlatformPostingResult:
        """Publishes message to Discord channel via incoming webhook."""
        if not self.webhook_url:
            if settings.MOCK_POSTING:
                # Sandbox simulation
                fake_msg_id = uuid.uuid4().hex[:18]
                posted_url = f"https://discord.com/channels/@me/{fake_msg_id}"
                logger.info("[MOCK] Discord post succeeded: %s", posted_url)
                return self._build_success_result(posted_url)
            return self._build_failure_result("Authentication failed: Missing DISCORD_WEBHOOK_URL.")

        try:
            # Append ?wait=true to receive published message details
            target_url = self.webhook_url
            if "?" not in target_url:
                target_url += "?wait=true"
            elif "wait=" not in target_url:
                target_url += "&wait=true"

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(target_url, json={"content": message})
                resp.raise_for_status()
                data = resp.json()
                msg_id = data.get("id", uuid.uuid4().hex[:16])
                channel_id = data.get("channel_id", "channel")
                posted_url = f"https://discord.com/channels/{channel_id}/{msg_id}"
                return self._build_success_result(posted_url)
        except httpx.HTTPStatusError as e:
            return self._build_failure_result(f"Discord API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            return self._build_failure_result(f"Discord connection error: {str(e)}")
