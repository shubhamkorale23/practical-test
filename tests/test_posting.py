"""Integration and unit tests for the Automated Multi-Platform Posting API."""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.platforms.discord import DiscordPlatform
from app.platforms.slack import SlackPlatform
from app.schemas.posting import PlatformPostingResult


@pytest.mark.asyncio
async def test_posting_endpoint_success():
    """Tests successful posting across all 5 platforms."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/posting",
            json={
                "message": "Check out our latest business platform and grow your online visibility. https://example.com"
            },
        )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "results" in data
    results = data["results"]
    assert len(results) >= 5

    platforms_found = {r["platform"] for r in results}
    expected_platforms = {"Discord", "Telegram", "Slack", "Mastodon", "Dev.to"}
    assert expected_platforms.issubset(platforms_found)

    for item in results:
        assert item["status"] == "success"
        assert item["posted_url"] is not None
        assert isinstance(item["public_access"], bool)
        assert item["date"] is not None
        assert item["time"] is not None
        assert item["error"] is None


@pytest.mark.asyncio
async def test_posting_validation_exceeds_200_chars():
    """Tests rejection when message exceeds 200 characters."""
    long_msg = "X" * 190 + " https://example.com"  # 210 characters > 200 limit
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/posting",
            json={"message": long_msg},
        )
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert any("200 characters" in str(err) for err in data.get("details", []))


@pytest.mark.asyncio
async def test_posting_validation_missing_cta_link():
    """Tests rejection when message contains zero CTA links."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/posting",
            json={"message": "Explore our revolutionary new product today!"},
        )
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert any("exactly one CTA link" in str(err) for err in data.get("details", []))


@pytest.mark.asyncio
async def test_posting_validation_multiple_cta_links():
    """Tests rejection when message contains more than one CTA link."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/posting",
            json={"message": "Visit https://site-a.com and also https://site-b.com"},
        )
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert any("exactly one CTA link" in str(err) for err in data.get("details", []))


@pytest.mark.asyncio
async def test_posting_fault_tolerance_isolated_failure():
    """Tests that failure on one platform does not prevent other platforms from succeeding."""
    mock_slack_failure = PlatformPostingResult(
        platform="Slack",
        status="failed",
        posted_url=None,
        public_access=False,
        date=None,
        time=None,
        error="Slack Webhook rejected with HTTP 403 Forbidden",
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch.object(
            SlackPlatform,
            "post_message",
            new_callable=AsyncMock,
            return_value=mock_slack_failure,
        ):
            response = await client.post(
                "/posting",
                json={
                    "message": "Special promotional update for tech startups. https://example.com"
                },
            )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    slack_item = next(r for r in data["results"] if r["platform"] == "Slack")
    assert slack_item["status"] == "failed"
    assert "Slack Webhook rejected" in slack_item["error"]
    assert slack_item["posted_url"] is None

    # Verify other platforms succeeded
    other_items = [r for r in data["results"] if r["platform"] != "Slack"]
    assert len(other_items) >= 4
    for other in other_items:
        assert other["status"] == "success"
        assert other["posted_url"] is not None
