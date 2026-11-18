"""Configuration settings for the application using Pydantic Settings."""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application configuration
    APP_NAME: str = "AI-Powered Website Analysis & Multi-Platform Posting API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 4000

    # Website Extractor Configuration
    REQUEST_TIMEOUT: float = 15.0
    MAX_REDIRECTS: int = 5
    MAX_PAGE_BYTES: int = 5 * 1024 * 1024  # 5 MB safety limit
    USER_AGENT: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36 (LinkAnalyzer/1.0)"
    )

    # LLM Configuration
    # Supported providers: "gemini", "openai", "anthropic", "auto", "heuristic"
    LLM_PROVIDER: str = "auto"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-haiku-20241022"
    LLM_TIMEOUT: float = 30.0

    # Multi-Platform Posting Configuration
    # When MOCK_POSTING is True, platforms without valid credentials will simulate
    # posting in a realistic sandbox environment. When False, unconfigured platforms
    # will report authentication/configuration errors.
    MOCK_POSTING: bool = True
    DISCORD_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None
    MASTODON_INSTANCE_URL: Optional[str] = "https://mastodon.social"
    MASTODON_ACCESS_TOKEN: Optional[str] = None
    DEVTO_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.example"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
