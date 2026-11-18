"""Pydantic schemas for the Link Analysis API."""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class LinkAnalysisRequest(BaseModel):
    """Request payload for website link analysis."""
    url: str = Field(
        ...,
        description="The website URL to analyze (must begin with http:// or https://).",
        examples=["https://example.com"]
    )

    @field_validator("url")
    @classmethod
    def check_url(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("URL cannot be empty.")
        v_stripped = v.strip()
        if not (v_stripped.startswith("http://") or v_stripped.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return v_stripped


class BrandDetails(BaseModel):
    """Section 1 Core Brand Information."""
    name: str = Field(..., description="Brand or business name.")
    category: str = Field(..., description="Main business category or industry.")
    summary: str = Field(..., description="Concise business overview and value proposition.")


class CompetitorItem(BaseModel):
    """Detailed competitor comparison entry."""
    name: str = Field(..., description="Competitor brand name.")
    service: str = Field(..., description="Main competitor service.")
    target_market: str = Field(..., description="Competitor target market.")
    strength: str = Field(..., description="Key competitor strength.")
    weakness: str = Field(..., description="Competitor weakness or market gap.")


class CompetitorAnalysis(BaseModel):
    """Section 1: Competitor vs Your Brand Details."""
    brand_overview: str = Field(..., description="Comprehensive overview of your brand.")
    competitors: List[CompetitorItem] = Field(
        default_factory=list,
        description="Minimum 3 identified competitors with comparative attributes."
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Your brand's key competitive advantages."
    )
    opportunities: List[str] = Field(
        default_factory=list,
        description="Opportunities to improve market positioning."
    )


class TargetSearchQuery(BaseModel):
    """Section 2: Target search query entry."""
    query: str = Field(..., description="Relevant search query potential customers use.")
    platforms: List[str] = Field(
        default_factory=list,
        description="Platforms where this query is suitable (Google, Facebook, Instagram, LinkedIn, X)."
    )
    intent: str = Field(
        ...,
        description="Search intent (e.g., Service Discovery, B2B Search, Inspiration, Commercial Intent)."
    )
    business_relevance: Optional[str] = Field(
        None,
        description="Relevance to website services and products."
    )
    target_audience: Optional[str] = Field(
        None,
        description="Target audience likely to submit this query."
    )


class SeoImprovements(BaseModel):
    """Section 3: SEO Improvement recommendations."""
    primary_keyword: str = Field(..., description="Primary recommended target keyword.")
    secondary_keywords: List[str] = Field(
        default_factory=list,
        description="Secondary supporting keywords."
    )
    long_tail_keywords: List[str] = Field(
        default_factory=list,
        description="Specific long-tail keywords with clear conversion intent."
    )
    relevant_business_keywords: List[str] = Field(
        default_factory=list,
        description="Relevant business category keywords."
    )
    recommended_title: str = Field(
        ...,
        description="Recommended optimized HTML title tag (50-60 characters)."
    )
    title_structure: Optional[str] = Field(
        None,
        description="Structural formula used for the title tag."
    )
    meta_description: str = Field(
        ...,
        description="Recommended human-friendly meta description (150-160 characters)."
    )
    supporting_content: List[str] = Field(
        default_factory=list,
        description="Recommended additional website content to improve search visibility."
    )


class ServiceItem(BaseModel):
    """Section 4: Top Service item."""
    service_name: str = Field(..., description="Name of the service.")
    description: str = Field(..., description="Short explanation of the service.")
    target_industry: str = Field(..., description="Relevant business industry.")
    target_customer: str = Field(..., description="Potential customer type.")
    main_benefit: str = Field(..., description="Why customers need this service.")
    is_inferred: bool = Field(
        default=False,
        description="True if inferred by AI; False if extracted directly from site content."
    )


class TargetAudience(BaseModel):
    """Section 5: Target Audience Identification."""
    primary_audience: List[str] = Field(
        default_factory=list,
        description="Primary target customer profiles."
    )
    secondary_audience: List[str] = Field(
        default_factory=list,
        description="Secondary target customer profiles."
    )
    industries: List[str] = Field(
        default_factory=list,
        description="Key industry segments."
    )
    business_types: List[str] = Field(
        default_factory=list,
        description="Business types (e.g., Small Businesses, Startups, Enterprise Companies)."
    )
    customer_profiles: List[str] = Field(
        default_factory=list,
        description="Detailed customer persona profiles."
    )
    location_focus: Optional[str] = Field(
        None,
        description="Geographical focus if detected or available."
    )
    customer_needs: List[str] = Field(
        default_factory=list,
        description="Customer pain points, requirements, and challenges."
    )
    customer_interests: List[str] = Field(
        default_factory=list,
        description="Potential customer interests."
    )
    recommended_segments: List[str] = Field(
        default_factory=list,
        description="Recommended audience segments for marketing campaigns."
    )


class FullAnalysis(BaseModel):
    """Container for all five analysis sections."""
    competitor_analysis: CompetitorAnalysis
    target_search_queries: List[TargetSearchQuery]
    seo_improvements: SeoImprovements
    top_services: List[ServiceItem]
    target_audience: TargetAudience


class LinkAnalysisResponse(BaseModel):
    """Standardized response for POST /link-analysis."""
    success: bool = True
    website: str
    brand: BrandDetails
    analysis: FullAnalysis
