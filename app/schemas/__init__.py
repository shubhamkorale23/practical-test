"""Pydantic schemas package."""

from app.schemas.link_analysis import (
    LinkAnalysisRequest,
    LinkAnalysisResponse,
    BrandDetails,
    CompetitorAnalysis,
    CompetitorItem,
    TargetSearchQuery,
    SeoImprovements,
    ServiceItem,
    TargetAudience,
    FullAnalysis,
)
from app.schemas.posting import (
    PostingRequest,
    PostingResponse,
    PlatformPostingResult,
)

__all__ = [
    "LinkAnalysisRequest",
    "LinkAnalysisResponse",
    "BrandDetails",
    "CompetitorAnalysis",
    "CompetitorItem",
    "TargetSearchQuery",
    "SeoImprovements",
    "ServiceItem",
    "TargetAudience",
    "FullAnalysis",
    "PostingRequest",
    "PostingResponse",
    "PlatformPostingResult",
]
