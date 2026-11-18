"""Dev.to / Forem API integration adapter."""

import logging
import random
import httpx

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas.posting import PlatformPostingResult

logger = logging.getLogger(__name__)


class DevToPlatform(BasePlatform):
    """Publishes developer announcements via Dev.to (Forem) API."""

    def __init__(self, api_key: str = None):
        super().__init__(name="Dev.to", is_public=True)
        self.api_key = api_key or settings.DEVTO_API_KEY

    async def post_message(self, message: str) -> PlatformPostingResult:
        """Publishes post / announcement to Dev.to."""
        if not self.api_key:
            if settings.MOCK_POSTING:
                fake_id = random.randint(100000, 999999)
                posted_url = f"https://dev.to/announcements/quick-update-{fake_id}"
                logger.info("[MOCK] Dev.to post succeeded: %s", posted_url)
                return self._build_success_result(posted_url)
            return self._build_failure_result("Authentication failed: Missing DEVTO_API_KEY.")

        try:
            url = "https://dev.to/api/articles"
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json",
            }
            # Dev.to expects title and body_markdown
            title_sample = message.split(".")[0][:80] or "Announcement"
            payload = {
                "article": {
                    "title": title_sample,
                    "published": True,
                    "body_markdown": message,
                    "tags": ["technology", "announcement"],
                }
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                posted_url = data.get("url") or f"https://dev.to/post/{data.get('id')}"
                return self._build_success_result(posted_url)
        except httpx.HTTPStatusError as e:
            return self._build_failure_result(f"Dev.to API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            return self._build_failure_result(f"Dev.to connection error: {str(e)}")
