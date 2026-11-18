"""Website analysis orchestration service."""

import logging
from app.schemas.link_analysis import LinkAnalysisResponse
from app.services.llm_service import LLMService
from app.services.website_extractor import WebsiteExtractor

logger = logging.getLogger(__name__)


class AnalysisService:
    """Orchestrates website extraction and AI-driven business intelligence analysis."""

    def __init__(self, extractor: WebsiteExtractor = None, llm_service: LLMService = None):
        self.extractor = extractor or WebsiteExtractor()
        self.llm_service = llm_service or LLMService()

    async def run_analysis(self, url: str) -> LinkAnalysisResponse:
        """Executes full link analysis workflow:

        1. SSRF check & HTML fetch
        2. Content parsing & extraction
        3. Token optimization & cleaning
        4. LLM / Heuristic intelligence generation
        5. Pydantic validation & response packaging

        Args:
            url: Validated public website URL.

        Returns:
            LinkAnalysisResponse conforming to prompt specifications.
        """
        logger.info("Starting link analysis for URL: %s", url)

        # Step 1 & 2: Fetch and extract HTML content
        extracted_content = await self.extractor.extract_from_url(url)

        # Step 3 & 4: LLM or Heuristic processing
        analysis_result = await self.llm_service.analyze_website(extracted_content)

        logger.info(
            "Successfully completed link analysis for '%s' (Brand: %s)",
            url,
            analysis_result.brand.name,
        )
        return analysis_result
