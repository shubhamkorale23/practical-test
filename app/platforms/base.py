"""Abstract base class and contract for third-party posting platform integrations."""

import abc
from datetime import datetime
from typing import Optional
import httpx

from app.config import settings
from app.schemas.posting import PlatformPostingResult


class BasePlatform(abc.ABC):
    """Abstract interface defining required behavior for each publishing platform."""

    def __init__(self, name: str, is_public: bool):
        self.name = name
        self.is_public = is_public

    @abc.abstractmethod
    async def post_message(self, message: str) -> PlatformPostingResult:
        """Publishes the message to the third-party platform.

        Args:
            message: Validated message containing exactly one CTA link.

        Returns:
            PlatformPostingResult detailing success/failure, date, time, and posted URL.
        """
        pass

    def _get_current_timestamp(self) -> tuple[str, str]:
        """Returns current date (YYYY-MM-DD) and time (HH:MM:SS)."""
        now = datetime.now()
        return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

    def _build_success_result(self, posted_url: str) -> PlatformPostingResult:
        """Helper to create a successful posting result."""
        date_str, time_str = self._get_current_timestamp()
        return PlatformPostingResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=self.is_public,
            date=date_str,
            time=time_str,
            error=None,
        )

    def _build_failure_result(self, error_message: str) -> PlatformPostingResult:
        """Helper to create a failed posting result."""
        return PlatformPostingResult(
            platform=self.name,
            status="failed",
            posted_url=None,
            public_access=False,
            date=None,
            time=None,
            error=error_message,
        )
