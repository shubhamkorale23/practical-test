"""Website content extraction service using HTTPX and BeautifulSoup."""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.utils.validators import validate_ssrf_safe_url

logger = logging.getLogger(__name__)


@dataclass
class ExtractedContent:
    """Structured information extracted from website HTML."""
    url: str
    domain: str
    status_code: int
    title: str = ""
    meta_description: str = ""
    meta_keywords: List[str] = field(default_factory=list)
    og_data: Dict[str, str] = field(default_factory=dict)
    headings_h1: List[str] = field(default_factory=list)
    headings_h2: List[str] = field(default_factory=list)
    headings_h3: List[str] = field(default_factory=list)
    clean_text: str = ""
    navigation_links: List[str] = field(default_factory=list)
    potential_services: List[str] = field(default_factory=list)
    brand_hint: str = ""

    def get_condensed_summary(self, max_length: int = 4000) -> str:
        """Returns a token-optimized summary of the website content for LLM ingestion.

        Cost optimization: Truncates and prioritizes high-signal content
        (title, meta, headings, service hints, and top paragraphs) to avoid
        spending tokens on boilerplate or repetitive text.
        """
        parts = [
            f"URL: {self.url}",
            f"Domain: {self.domain}",
            f"Title: {self.title}",
            f"Meta Description: {self.meta_description}",
        ]
        if self.headings_h1:
            parts.append(f"Main Headings (H1): {'; '.join(self.headings_h1[:5])}")
        if self.headings_h2:
            parts.append(f"Subheadings (H2): {'; '.join(self.headings_h2[:8])}")
        if self.potential_services:
            parts.append(f"Extracted Services/Features: {'; '.join(self.potential_services[:10])}")
        if self.clean_text:
            remaining_budget = max_length - sum(len(p) for p in parts)
            if remaining_budget > 200:
                truncated_text = self.clean_text[:remaining_budget]
                parts.append(f"Body Content:\n{truncated_text}")

        return "\n\n".join(parts)


class WebsiteExtractor:
    """Extracts, cleans, and structures content from a target URL."""

    def __init__(
        self,
        timeout: float = settings.REQUEST_TIMEOUT,
        max_redirects: int = settings.MAX_REDIRECTS,
        max_bytes: int = settings.MAX_PAGE_BYTES,
        user_agent: str = settings.USER_AGENT,
    ):
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.max_bytes = max_bytes
        self.user_agent = user_agent

    async def fetch_html(self, url: str) -> tuple[str, int]:
        """Fetches website HTML asynchronously while enforcing SSRF checks.

        Args:
            url: Validated public website URL.

        Returns:
            Tuple of (html_text, status_code).

        Raises:
            ValueError: If SSRF check fails or response is not HTML.
            httpx.HTTPError: If network request fails or times out.
        """
        # Validate SSRF safety before initiating HTTP connection
        validated_url = validate_ssrf_safe_url(url)

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            max_redirects=self.max_redirects,
            verify=True,
        ) as client:
            try:
                response = await client.get(validated_url, headers=headers)
            except httpx.ConnectTimeout:
                raise ValueError(f"Connection timed out while attempting to reach {url}.")
            except httpx.ConnectError as e:
                raise ValueError(f"Unable to connect to website {url}: {str(e)}")
            except httpx.RequestError as e:
                raise ValueError(f"Failed to fetch website {url}: {str(e)}")

        if response.status_code >= 400:
            raise ValueError(
                f"Website responded with HTTP status code {response.status_code}."
            )

        content_type = response.headers.get("content-type", "").lower()
        if content_type and not any(t in content_type for t in ("text/html", "application/xhtml+xml", "text/plain")):
            raise ValueError(
                f"URL does not appear to be an HTML webpage (Content-Type: '{content_type}')."
            )

        if len(response.content) > self.max_bytes:
            # Safely truncate excess bytes
            html = response.text[: self.max_bytes]
        else:
            html = response.text

        return html, response.status_code

    def extract_content(self, url: str, html: str, status_code: int = 200) -> ExtractedContent:
        """Parses HTML and extracts structured content.

        Args:
            url: The source URL.
            html: Raw HTML string.
            status_code: HTTP response status code.

        Returns:
            ExtractedContent instance with cleaned signals.
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        soup = BeautifulSoup(html, "html.parser")

        # 1. Extract Title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("meta", property="og:title"):
            title = soup.find("meta", property="og:title").get("content", "").strip()

        # 2. Extract Meta Description & Keywords
        meta_description = ""
        meta_desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
        if not meta_desc_tag:
            meta_desc_tag = soup.find("meta", attrs={"property": "og:description"})
        if meta_desc_tag and meta_desc_tag.get("content"):
            meta_description = meta_desc_tag.get("content").strip()

        meta_keywords = []
        meta_key_tag = soup.find("meta", attrs={"name": re.compile(r"^keywords$", re.I)})
        if meta_key_tag and meta_key_tag.get("content"):
            raw_keywords = meta_key_tag.get("content")
            meta_keywords = [k.strip() for k in raw_keywords.split(",") if k.strip()]

        # 3. Open Graph data
        og_data = {}
        for og_tag in soup.find_all("meta", property=re.compile(r"^og:")):
            prop = og_tag.get("property", "")
            content = og_tag.get("content", "")
            if prop and content:
                og_data[prop] = content.strip()

        # Derive brand hint
        brand_hint = og_data.get("og:site_name", "")
        if not brand_hint and title:
            # Often titles are structured as "Page Title - Brand Name" or "Brand | Tagline"
            if " - " in title:
                brand_hint = title.split(" - ")[-1].strip()
            elif " | " in title:
                brand_hint = title.split(" | ")[0].strip()
        if not brand_hint:
            brand_hint = domain.split(".")[0].capitalize()

        # 4. Extract Headings
        headings_h1 = [
            h.get_text(strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)
        ]
        headings_h2 = [
            h.get_text(strip=True) for h in soup.find_all("h2") if h.get_text(strip=True)
        ]
        headings_h3 = [
            h.get_text(strip=True) for h in soup.find_all("h3") if h.get_text(strip=True)
        ]

        # 5. Extract Potential Services
        potential_services = []
        service_keywords = re.compile(r"service|solution|feature|product|offer|what we do", re.I)
        for heading in soup.find_all(["h2", "h3", "h4"]):
            if service_keywords.search(heading.get_text()):
                # Look for immediately following ul/ol or siblings
                next_list = heading.find_next(["ul", "ol"])
                if next_list:
                    for li in next_list.find_all("li", limit=8):
                        text = li.get_text(strip=True)
                        if 3 < len(text) < 100 and text not in potential_services:
                            potential_services.append(text)

                parent = heading.find_parent(["section", "div", "article", "main"])
                if parent:
                    for li in parent.find_all("li", limit=8):
                        text = li.get_text(strip=True)
                        if 3 < len(text) < 100 and text not in potential_services:
                            potential_services.append(text)

        # 6. Clean and extract main text body
        # Remove noisy tags: scripts, styles, svg, canvas, forms, footers, navs
        for unwanted in soup.find_all(
            ["script", "style", "noscript", "svg", "canvas", "iframe", "footer", "nav"]
        ):
            unwanted.decompose()

        paragraphs = []
        for p in soup.find_all(["p", "article", "section"]):
            p_text = p.get_text(separator=" ", strip=True)
            # Filter out boilerplate, short links, cookie notices
            if len(p_text) > 30 and not any(
                b in p_text.lower()
                for b in ["cookie", "privacy policy", "all rights reserved", "javascript is required"]
            ):
                paragraphs.append(p_text)

        clean_text = " ".join(paragraphs)
        # Collapse multiple whitespace
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        return ExtractedContent(
            url=url,
            domain=domain,
            status_code=status_code,
            title=title,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            og_data=og_data,
            headings_h1=headings_h1,
            headings_h2=headings_h2,
            headings_h3=headings_h3,
            clean_text=clean_text,
            potential_services=potential_services,
            brand_hint=brand_hint,
        )

    async def extract_from_url(self, url: str) -> ExtractedContent:
        """Helper combining fetch_html and extract_content."""
        html, status_code = await self.fetch_html(url)
        return self.extract_content(url, html, status_code)
