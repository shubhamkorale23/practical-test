"""Tests covering live HTTP branches and error states for all 5 posting platforms."""

from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest

from app.platforms.devto import DevToPlatform
from app.platforms.discord import DiscordPlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.slack import SlackPlatform
from app.platforms.telegram import TelegramPlatform


@pytest.mark.asyncio
async def test_discord_live_success():
    platform = DiscordPlatform(webhook_url="https://discord.com/api/webhooks/123/abc")
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": "999888", "channel_id": "777666"}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        res = await platform.post_message("Test message https://example.com")

    assert res.status == "success"
    assert "https://discord.com/channels/777666/999888" in res.posted_url
    assert res.error is None


@pytest.mark.asyncio
async def test_discord_live_http_error():
    platform = DiscordPlatform(webhook_url="https://discord.com/api/webhooks/123/abc")
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 404
    mock_resp.text = "Unknown Webhook"
    http_err = httpx.HTTPStatusError("404", request=MagicMock(), response=mock_resp)

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=http_err):
        res = await platform.post_message("Test message https://example.com")

    assert res.status == "failed"
    assert "404" in res.error


@pytest.mark.asyncio
async def test_telegram_live_success():
    platform = TelegramPlatform(bot_token="fake_token", chat_id="@mychannel")
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "ok": True,
        "result": {
            "message_id": 12345,
            "chat": {"username": "mychannel"},
        },
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        res = await platform.post_message("Test message https://example.com")

    assert res.status == "success"
    assert res.posted_url == "https://t.me/mychannel/12345"


@pytest.mark.asyncio
async def test_telegram_live_api_error():
    platform = TelegramPlatform(bot_token="fake_token", chat_id="@mychannel")
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "ok": False,
        "description": "Chat not found",
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        res = await platform.post_message("Test message https://example.com")

    assert res.status == "failed"
    assert "Chat not found" in res.error


@pytest.mark.asyncio
async def test_slack_live_success():
    platform = SlackPlatform(webhook_url="https://hooks.slack.com/services/T/B/X")
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.text = "ok"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        res = await platform.post_message("Test message https://example.com")

    assert res.status == "success"
    assert res.posted_url is not None


@pytest.mark.asyncio
async def test_slack_live_rejection():
    platform = SlackPlatform(webhook_url="https://hooks.slack.com/services/T/B/X")
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.text = "invalid_payload"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        res = await platform.post_message("Test message https://example.com")

    assert res.status == "failed"
    assert "rejected payload" in res.error


@pytest.mark.asyncio
async def test_mastodon_live_success():
    platform = MastodonPlatform(
        instance_url="https://mastodon.social",
        access_token="fake_token",
    )
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "111222333",
        "url": "https://mastodon.social/@user/111222333",
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        res = await platform.post_message("Test message https://example.com")

    assert res.status == "success"
    assert res.posted_url == "https://mastodon.social/@user/111222333"


@pytest.mark.asyncio
async def test_devto_live_success():
    platform = DevToPlatform(api_key="fake_key")
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 201
    mock_resp.json.return_value = {
        "id": 554433,
        "url": "https://dev.to/user/post-slug-554433",
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        res = await platform.post_message("Test message https://example.com")

    assert res.status == "success"
    assert res.posted_url == "https://dev.to/user/post-slug-554433"


@pytest.mark.asyncio
async def test_platforms_unconfigured_when_mock_disabled():
    with patch("app.config.settings.MOCK_POSTING", False):
        discord = DiscordPlatform(webhook_url=None)
        res_discord = await discord.post_message("msg https://example.com")
        assert res_discord.status == "failed"
        assert "Missing DISCORD_WEBHOOK_URL" in res_discord.error

        telegram = TelegramPlatform(bot_token=None, chat_id=None)
        res_telegram = await telegram.post_message("msg https://example.com")
        assert res_telegram.status == "failed"
        assert "Missing TELEGRAM_BOT_TOKEN" in res_telegram.error

        slack = SlackPlatform(webhook_url=None)
        res_slack = await slack.post_message("msg https://example.com")
        assert res_slack.status == "failed"
        assert "Missing SLACK_WEBHOOK_URL" in res_slack.error

        mastodon = MastodonPlatform(access_token=None)
        res_mastodon = await mastodon.post_message("msg https://example.com")
        assert res_mastodon.status == "failed"
        assert "Missing MASTODON_ACCESS_TOKEN" in res_mastodon.error

        devto = DevToPlatform(api_key=None)
        res_devto = await devto.post_message("msg https://example.com")
        assert res_devto.status == "failed"
        assert "Missing DEVTO_API_KEY" in res_devto.error
