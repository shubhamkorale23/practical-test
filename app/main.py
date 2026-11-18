"""FastAPI application entrypoint for AI-Powered Link Analysis and Multi-Platform Posting."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import link_analysis_router, posting_router
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle hook for startup and shutdown events."""
    logger.info("Initializing %s (v%s)...", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Server running at http://%s:%d", settings.HOST, settings.PORT)
    logger.info("API Docs available at http://localhost:%d/docs", settings.PORT)
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production REST API delivering two key capabilities:\n\n"
        "1. **AI-Powered Website Link Analysis (`POST /link-analysis`)**: "
        "Extracts and structures website content, analyzing competitors, target search queries across "
        "Google and social media, actionable SEO improvements, core services, and target audiences.\n\n"
        "2. **Automated Multi-Platform Posting (`POST /posting`)**: "
        "Validates and broadcasts short messages with a CTA link across Discord, Telegram, Slack, Mastodon, "
        "and Dev.to with isolated fault tolerance."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(link_analysis_router)
app.include_router(posting_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom exception handler for clean, descriptive validation errors."""
    errors = []
    for err in exc.errors():
        field_name = ".".join(str(loc) for loc in err.get("loc", []))
        message = err.get("msg", "Validation error")
        errors.append({"field": field_name, "message": message})

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Input validation failed",
            "details": errors,
        },
    )


@app.get("/", tags=["General"])
async def root():
    """Root endpoint providing service overview and documentation links."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "endpoints": {
            "link_analysis": {
                "method": "POST",
                "path": "/link-analysis",
                "description": "Analyzes website URL and returns 5 structured intelligence sections.",
                "example_request": {"url": "https://example.com"},
            },
            "multi_platform_posting": {
                "method": "POST",
                "path": "/posting",
                "description": "Publishes validated short message with CTA across 5 third-party platforms.",
                "example_request": {
                    "message": "Check out our latest business platform and grow your online visibility. https://example.com"
                },
            },
        },
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
