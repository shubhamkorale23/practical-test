"""Telegram Bot API integration adapter."""

import logging
import random
import httpx

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas.posting import PlatformPostingResult

logger = logging.getLogger(__name__)


class TelegramPlatform(BasePlatform):
    """Publishes messages via Telegram Bot API."""

    def __init__(self, bot_token: str = None, chat_id: str = None):
        super().__init__(name="Telegram", is_public=True)
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or settings.TELEGRAM_CHAT_ID

    async def post_message(self, message: str) -> PlatformPostingResult:
        """Publishes message to Telegram chat/channel."""
        if not self.bot_token or not self.chat_id:
            if settings.MOCK_POSTING:
                fake_msg_id = random.randint(1000, 99999)
                posted_url = f"https://t.me/public_announcements/{fake_msg_id}"
                logger.info("[MOCK] Telegram post succeeded: %s", posted_url)
                return self._build_success_result(posted_url)
            return self._build_failure_result("Authentication failed: Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID.")

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "disable_web_page_preview": False,
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                if not data.get("ok"):
                    return self._build_failure_result(f"Telegram API error: {data.get('description', 'Unknown error')}")

                result_data = data.get("result", {})
                message_id = result_data.get("message_id")
                chat_info = result_data.get("chat", {})
                username = chat_info.get("username")

                if username:
                    posted_url = f"https://t.me/{username}/{message_id}"
                else:
                    posted_url = f"https://t.me/c/{str(self.chat_id).replace('-100', '')}/{message_id}"

                return self._build_success_result(posted_url)
        except httpx.HTTPStatusError as e:
            return self._build_failure_result(f"Telegram API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            return self._build_failure_result(f"Telegram connection error: {str(e)}")
