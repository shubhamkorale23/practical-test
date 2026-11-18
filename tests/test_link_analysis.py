"""Integration and unit tests for the AI-Powered Link Analysis API."""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.website_extractor import ExtractedContent, WebsiteExtractor

SAMPLE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NexGen Cloud - Modern Enterprise Cloud & AI Solutions</title>
    <meta name="description" content="NexGen Cloud provides enterprise cloud computing, AI model deployment, and DevOps automation for high-growth tech companies.">
    <meta name="keywords" content="cloud computing, AI deployment, devops, kubernetes, serverless">
    <meta property="og:site_name" content="NexGen Cloud">
    <meta property="og:title" content="NexGen Cloud Enterprise Solutions">
    <meta property="og:description" content="Accelerate your digital transformation with high-performance cloud infrastructure.">
</head>
<body>
    <header>
        <h1>Next-Generation Cloud & AI Engineering</h1>
        <nav><a href="/about">About</a><a href="/services">Services</a></nav>
    </header>
    <main>
        <h2>Our Core Services & Solutions</h2>
        <section>
            <ul>
                <li>Managed Kubernetes & Cloud Migration</li>
                <li>Enterprise Generative AI Infrastructure</li>
                <li>Automated CI/CD DevOps Pipelines</li>
                <li>24/7 Cloud Security & Compliance Hardening</li>
                <li>Full-Stack Serverless Architecture Consulting</li>
            </ul>
        </section>
        <p>NexGen Cloud delivers battle-tested infrastructure engineering for growing enterprises. Our distributed team helps technology leaders modernize legacy monolithic applications into scalable, containerized microservices.</p>
        <p>With guaranteed 99.99% uptime SLAs and dedicated 24/7 technical architects, we eliminate engineering bottlenecks and reduce infrastructure expenses by up to 40%.</p>
    </main>
</body>
</html>
"""


@pytest.mark.asyncio
async def test_link_analysis_success():
    """Tests successful link analysis flow with all 5 functional sections verified."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Mock HTML fetch to return realistic sample webpage
        with patch.object(
            WebsiteExtractor,
            "fetch_html",
            new_callable=AsyncMock,
            return_value=(SAMPLE_HTML, 200),
        ):
            response = await client.post(
                "/link-analysis",
                json={"url": "https://nexgencloud.io"},
            )

    assert response.status_code == 200
    data = response.json()

    # Top-level structure verification
    assert data["success"] is True
    assert data["website"] == "https://nexgencloud.io"

    # Brand Details verification
    brand = data["brand"]
    assert "NexGen Cloud" in brand["name"]
    assert len(brand["category"]) > 0
    assert len(brand["summary"]) > 10

    analysis = data["analysis"]

    # Section 1: Competitor vs Your Brand Details
    comp_analysis = analysis["competitor_analysis"]
    assert len(comp_analysis["brand_overview"]) > 10
    assert len(comp_analysis["competitors"]) >= 3
    for comp in comp_analysis["competitors"]:
        assert len(comp["name"]) > 0
        assert len(comp["service"]) > 0
        assert len(comp["strength"]) > 0
        assert len(comp["weakness"]) > 0
    assert len(comp_analysis["strengths"]) > 0
    assert len(comp_analysis["opportunities"]) > 0

    # Section 2: Top 5 Target Search Queries
    queries = analysis["target_search_queries"]
    assert len(queries) == 5
    for q in queries:
        assert len(q["query"]) > 0
        assert len(q["platforms"]) > 0
        assert len(q["intent"]) > 0
        assert len(q["business_relevance"]) > 0
        assert len(q["target_audience"]) > 0

    # Section 3: SEO Improvement
    seo = analysis["seo_improvements"]
    assert len(seo["primary_keyword"]) > 0
    assert len(seo["secondary_keywords"]) > 0
    assert len(seo["long_tail_keywords"]) > 0
    assert len(seo["relevant_business_keywords"]) > 0
    assert len(seo["recommended_title"]) > 0
    assert len(seo["meta_description"]) > 0
    assert len(seo["supporting_content"]) > 0

    # Section 4: Top 5 Services
    services = analysis["top_services"]
    assert len(services) == 5
    for s in services:
        assert len(s["service_name"]) > 0
        assert len(s["description"]) > 0
        assert len(s["target_industry"]) > 0
        assert len(s["target_customer"]) > 0
        assert len(s["main_benefit"]) > 0
        assert isinstance(s["is_inferred"], bool)

    # Section 5: Target Audience Identification
    aud = analysis["target_audience"]
    assert len(aud["primary_audience"]) > 0
    assert len(aud["secondary_audience"]) > 0
    assert len(aud["industries"]) > 0
    assert len(aud["business_types"]) > 0
    assert len(aud["customer_profiles"]) > 0
    assert len(aud["customer_needs"]) > 0
    assert len(aud["customer_interests"]) > 0
    assert len(aud["recommended_segments"]) > 0


@pytest.mark.asyncio
async def test_link_analysis_invalid_scheme():
    """Tests rejection of invalid or non-HTTP schemes."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/link-analysis",
            json={"url": "ftp://example.com/file"},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_link_analysis_ssrf_blocked_localhost():
    """Tests SSRF defense blocking requests to localhost and private addresses."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/link-analysis",
            json={"url": "http://localhost:8080/internal"},
        )
    assert response.status_code == 400
    assert "SSRF protection" in response.json()["detail"]


@pytest.mark.asyncio
async def test_link_analysis_ssrf_blocked_private_ip():
    """Tests SSRF defense blocking requests to private RFC-1918 IPs."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/link-analysis",
            json={"url": "http://192.168.1.1/admin"},
        )
    assert response.status_code == 400
    assert "SSRF protection" in response.json()["detail"]


@pytest.mark.asyncio
async def test_link_analysis_inaccessible_website():
    """Tests graceful handling when remote website returns 404 or connection failure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch.object(
            WebsiteExtractor,
            "fetch_html",
            new_callable=AsyncMock,
            side_effect=ValueError("Website responded with HTTP status code 404."),
        ):
            response = await client.post(
                "/link-analysis",
                json={"url": "https://broken-website.example"},
            )
    assert response.status_code == 400
    assert "404" in response.json()["detail"]


def test_website_extractor_parsing():
    """Unit test for BeautifulSoup HTML content extraction."""
    extractor = WebsiteExtractor()
    extracted = extractor.extract_content("https://nexgencloud.io", SAMPLE_HTML)

    assert extracted.brand_hint == "NexGen Cloud"
    assert "NexGen Cloud" in extracted.title
    assert "enterprise cloud computing" in extracted.meta_description
    assert len(extracted.headings_h1) == 1
    assert "Next-Generation Cloud" in extracted.headings_h1[0]
    assert len(extracted.potential_services) >= 3
    assert "Managed Kubernetes" in extracted.potential_services[0]
    assert len(extracted.clean_text) > 100
