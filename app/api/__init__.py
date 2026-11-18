"""API routes package."""

from app.api.routes_link_analysis import router as link_analysis_router
from app.api.routes_posting import router as posting_router

__all__ = ["link_analysis_router", "posting_router"]
