"""Posting orchestration service across multiple third-party platforms."""

import asyncio
import logging
from typing import List

from app.platforms import (
    BasePlatform,
    DevToPlatform,
    DiscordPlatform,
    MastodonPlatform,
    SlackPlatform,
    TelegramPlatform,
)
from app.schemas.posting import PlatformPostingResult, PostingResponse

logger = logging.getLogger(__name__)


class PostingService:
    """Orchestrates independent, concurrent message distribution across all platforms."""

    def __init__(self, platforms: List[BasePlatform] = None):
        if platforms is not None:
            self.platforms = platforms
        else:
            self.platforms = [
                DiscordPlatform(),
                TelegramPlatform(),
                SlackPlatform(),
                MastodonPlatform(),
                DevToPlatform(),
            ]

    async def post_to_all(self, message: str) -> PostingResponse:
        """Publishes the message to each platform independently and concurrently.

        Fault Isolation: Each platform task is wrapped to prevent one platform's
        failure from disrupting the others.

        Args:
            message: Validated message string.

        Returns:
            PostingResponse containing results for all platforms.
        """
        tasks = [self._safe_post(p, message) for p in self.platforms]
        results = await asyncio.gather(*tasks)

        logger.info(
            "Posting cycle finished for %d platforms: %d succeeded, %d failed",
            len(results),
            sum(1 for r in results if r.status == "success"),
            sum(1 for r in results if r.status == "failed"),
        )

        return PostingResponse(success=True, results=results)

    async def _safe_post(self, platform: BasePlatform, message: str) -> PlatformPostingResult:
        """Executes posting with exception containment."""
        try:
            return await platform.post_message(message)
        except Exception as e:
            logger.error("Unhandled error posting to %s: %s", platform.name, str(e), exc_info=True)
            return platform._build_failure_result(f"Internal platform error: {str(e)}")
