"""Unit tests for LLMService provider adapters and root/health routes."""

from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.competitor_service import CompetitorService
from app.services.llm_service import LLMService
from app.services.website_extractor import ExtractedContent


@pytest.fixture
def sample_extracted():
    return ExtractedContent(
        url="https://sample.com",
        domain="sample.com",
        status_code=200,
        title="Sample AI Platform",
        meta_description="Sample description for testing.",
        clean_text="Body content for testing.",
        brand_hint="Sample AI",
    )


VALID_ANALYSIS_JSON = {
    "brand": {
        "name": "Sample AI",
        "category": "Artificial Intelligence",
        "summary": "Sample AI summary",
    },
    "analysis": {
        "competitor_analysis": {
            "brand_overview": "Overview text",
            "competitors": [
                {
                    "name": "Comp 1",
                    "service": "Service A",
                    "target_market": "Market A",
                    "strength": "Fast",
                    "weakness": "Costly",
                },
                {
                    "name": "Comp 2",
                    "service": "Service B",
                    "target_market": "Market B",
                    "strength": "Large",
                    "weakness": "Complex",
                },
                {
                    "name": "Comp 3",
                    "service": "Service C",
                    "target_market": "Market C",
                    "strength": "Cheap",
                    "weakness": "Slow",
                },
            ],
            "strengths": ["Innovation"],
            "opportunities": ["Global expansion"],
        },
        "target_search_queries": [
            {
                "query": "best sample ai",
                "platforms": ["Google"],
                "intent": "Discovery",
                "business_relevance": "Core service",
                "target_audience": "Tech leads",
            }
        ],
        "seo_improvements": {
            "primary_keyword": "Sample AI",
            "secondary_keywords": ["Machine Learning"],
            "long_tail_keywords": ["best sample ai for teams"],
            "relevant_business_keywords": ["AI APIs"],
            "recommended_title": "Sample AI Platform",
            "title_structure": "Brand | Category",
            "meta_description": "Sample meta description for testing.",
            "supporting_content": ["Case studies"],
        },
        "top_services": [
            {
                "service_name": "AI Processing",
                "description": "Core AI model inference.",
                "target_industry": "Tech",
                "target_customer": "Developers",
                "main_benefit": "Speed",
                "is_inferred": False,
            }
        ],
        "target_audience": {
            "primary_audience": ["Developers"],
            "secondary_audience": ["Managers"],
            "industries": ["Tech"],
            "business_types": ["Startups"],
            "customer_profiles": ["Engineers"],
            "location_focus": "Global",
            "customer_needs": ["Speed"],
            "customer_interests": ["AI"],
            "recommended_segments": ["Early stage"],
        },
    },
}


@pytest.mark.asyncio
async def test_llm_gemini_provider(sample_extracted):
    llm = LLMService()
    llm.provider = "gemini"
    llm.gemini_key = "fake_gemini_key"

    import json
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": json.dumps(VALID_ANALYSIS_JSON)}]}}
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        res = await llm.analyze_website(sample_extracted)

    assert res.success is True
    assert res.brand.name == "Sample AI"


@pytest.mark.asyncio
async def test_llm_openai_provider(sample_extracted):
    llm = LLMService()
    llm.provider = "openai"
    llm.openai_key = "fake_openai_key"

    import json
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {"message": {"content": json.dumps(VALID_ANALYSIS_JSON)}}
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        res = await llm.analyze_website(sample_extracted)

    assert res.success is True
    assert res.brand.name == "Sample AI"


@pytest.mark.asyncio
async def test_llm_anthropic_provider(sample_extracted):
    llm = LLMService()
    llm.provider = "anthropic"
    llm.anthropic_key = "fake_anthropic_key"

    import json
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "content": [
            {"text": f"```json\n{json.dumps(VALID_ANALYSIS_JSON)}\n```"}
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        res = await llm.analyze_website(sample_extracted)

    assert res.success is True
    assert res.brand.name == "Sample AI"


def test_competitor_service():
    comps = CompetitorService.identify_market_position("Cloud Services", "TestBrand")
    assert len(comps) == 3
    assert comps[0].name is not None


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "endpoints" in data
    assert "/link-analysis" in str(data)
    assert "/posting" in str(data)


@pytest.mark.asyncio
async def test_health_check_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
