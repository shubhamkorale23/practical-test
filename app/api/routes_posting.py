"""API route for Automated Multi-Platform Message Posting."""

import logging
from fastapi import APIRouter, HTTPException, status

from app.schemas.posting import PostingRequest, PostingResponse
from app.services.posting_service import PostingService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Multi-Platform Posting"])
posting_service = PostingService()


@router.post(
    "/posting",
    response_model=PostingResponse,
    status_code=status.HTTP_200_OK,
    summary="Publish short message across multiple platforms",
    description=(
        "Publishes a short message (max 200 characters with exactly one CTA link) "
        "across 5 third-party platforms (Discord, Telegram, Slack, Mastodon, Dev.to). "
        "Platforms are handled independently so that failure on one does not disrupt others."
    ),
)
async def post_message_to_platforms(payload: PostingRequest) -> PostingResponse:
    """Dispatches validated message across all configured platforms."""
    try:
        response = await posting_service.post_to_all(payload.message)
        return response
    except Exception as e:
        logger.error("Unexpected error in posting service: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during multi-platform posting: {str(e)}",
        )
