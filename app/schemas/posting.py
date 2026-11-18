"""Pydantic schemas for the Automated Multi-Platform Posting API."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.utils.validators import validate_posting_message


class PostingRequest(BaseModel):
    """Request payload for multi-platform message publication."""
    message: str = Field(
        ...,
        description="Short message to publish across platforms (max 200 chars, exactly one CTA link).",
        examples=[
            "Check out our latest business platform and grow your online visibility. https://example.com"
        ]
    )

    @field_validator("message")
    @classmethod
    def validate_message_rules(cls, v: str) -> str:
        """Enforces length limit, exactly one CTA link, and URL validity."""
        cleaned_msg, _ = validate_posting_message(v)
        return cleaned_msg


class PlatformPostingResult(BaseModel):
    """Result of publishing to an individual platform."""
    platform: str = Field(..., description="Platform name.")
    status: str = Field(..., description="Publication status ('success' or 'failed').")
    posted_url: Optional[str] = Field(None, description="Published content URL if successful.")
    public_access: bool = Field(..., description="Whether content is publicly accessible.")
    date: Optional[str] = Field(None, description="Posting date (YYYY-MM-DD).")
    time: Optional[str] = Field(None, description="Posting time (HH:MM:SS).")
    error: Optional[str] = Field(None, description="Error details if publication failed.")


class PostingResponse(BaseModel):
    """Standardized response for POST /posting."""
    success: bool = True
    results: List[PlatformPostingResult] = Field(
        ...,
        description="Independent publication outcomes for all platforms."
    )
