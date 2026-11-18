"""API route for AI-Powered Website Link Analysis."""

import logging
from fastapi import APIRouter, HTTPException, status

from app.schemas.link_analysis import LinkAnalysisRequest, LinkAnalysisResponse
from app.services.analysis_service import AnalysisService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Link Analysis"])
analysis_service = AnalysisService()


@router.post(
    "/link-analysis",
    response_model=LinkAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze website link with AI",
    description=(
        "Analyzes a submitted website URL, understands its business and content, "
        "and generates competitor intelligence, top 5 search queries across Google/social platforms, "
        "practical SEO improvements, top 5 services, and target audience segments."
    ),
)
async def analyze_link(payload: LinkAnalysisRequest) -> LinkAnalysisResponse:
    """Processes a website URL and returns 5 structured analysis sections."""
    try:
        result = await analysis_service.run_analysis(payload.url)
        return result
    except ValueError as e:
        logger.warning("Validation or fetch error for URL '%s': %s", payload.url, str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Unexpected error analyzing URL '%s': %s", payload.url, str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the website: {str(e)}",
        )
