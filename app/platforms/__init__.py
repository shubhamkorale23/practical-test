"""Supported multi-platform integrations."""

from app.platforms.base import BasePlatform
from app.platforms.discord import DiscordPlatform
from app.platforms.telegram import TelegramPlatform
from app.platforms.slack import SlackPlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.devto import DevToPlatform

__all__ = [
    "BasePlatform",
    "DiscordPlatform",
    "TelegramPlatform",
    "SlackPlatform",
    "MastodonPlatform",
    "DevToPlatform",
]
