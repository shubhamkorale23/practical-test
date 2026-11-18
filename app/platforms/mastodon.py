"""Mastodon Statuses API integration adapter."""

import logging
import random
import httpx

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas.posting import PlatformPostingResult

logger = logging.getLogger(__name__)


class MastodonPlatform(BasePlatform):
    """Publishes messages via Mastodon Statuses API."""

    def __init__(self, instance_url: str = None, access_token: str = None):
        super().__init__(name="Mastodon", is_public=True)
        self.instance_url = (instance_url or settings.MASTODON_INSTANCE_URL).rstrip("/")
        self.access_token = access_token or settings.MASTODON_ACCESS_TOKEN

    async def post_message(self, message: str) -> PlatformPostingResult:
        """Publishes public status update (toot) to Mastodon instance."""
        if not self.access_token:
            if settings.MOCK_POSTING:
                fake_status_id = random.randint(110000000000000000, 119999999999999999)
                posted_url = f"{self.instance_url}/@announcements/{fake_status_id}"
                logger.info("[MOCK] Mastodon post succeeded: %s", posted_url)
                return self._build_success_result(posted_url)
            return self._build_failure_result("Authentication failed: Missing MASTODON_ACCESS_TOKEN.")

        try:
            url = f"{self.instance_url}/api/v1/statuses"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "status": message,
                "visibility": "public",
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                posted_url = data.get("url") or f"{self.instance_url}/notice/{data.get('id')}"
                return self._build_success_result(posted_url)
        except httpx.HTTPStatusError as e:
            return self._build_failure_result(f"Mastodon API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            return self._build_failure_result(f"Mastodon connection error: {str(e)}")
