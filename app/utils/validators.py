"""Validation utilities for URLs, SSRF protection, and message constraints."""

import ipaddress
import re
import socket
from typing import List, Tuple
from urllib.parse import urlparse

# Strict URL regex pattern
URL_REGEX = re.compile(
    r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d+)?(?:/[^\s]*)?",
    re.IGNORECASE,
)


def validate_url_format(url: str) -> str:
    """Validates the basic syntax and scheme of a URL.

    Args:
        url: URL string to validate.

    Returns:
        Cleaned, stripped URL string.

    Raises:
        ValueError: If URL is malformed or uses an unsupported scheme.
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL cannot be empty.")

    clean_url = url.strip()
    parsed = urlparse(clean_url)

    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError(
            f"Invalid URL scheme '{parsed.scheme}'. Only 'http' and 'https' are supported."
        )

    if not parsed.netloc:
        raise ValueError("URL must contain a valid domain or host.")

    # Remove credentials if embedded in URL (e.g., http://user:pass@example.com)
    if parsed.username or parsed.password:
        raise ValueError("URLs containing embedded user credentials are not allowed.")

    return clean_url


def is_safe_ip(ip_str: str) -> bool:
    """Checks whether an IP address is safe (not private, loopback, or reserved).

    Args:
        ip_str: IP address string (IPv4 or IPv6).

    Returns:
        True if IP is public and safe to request; False otherwise.
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        # Check against dangerous address spaces
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            return False
        return True
    except ValueError:
        return False


def validate_ssrf_safe_url(url: str) -> str:
    """Validates that a URL is safe against Server-Side Request Forgery (SSRF).

    Resolves domain to IP addresses and checks each address against private,
    loopback, link-local, and reserved ranges.

    Args:
        url: The website URL to validate.

    Returns:
        The validated URL string.

    Raises:
        ValueError: If the URL fails format validation or targets a non-public IP.
    """
    clean_url = validate_url_format(url)
    parsed = urlparse(clean_url)
    hostname = parsed.hostname

    if not hostname:
        raise ValueError("URL has an invalid hostname.")

    # Reject localhost or common internal names directly
    lower_host = hostname.lower()
    if lower_host in ("localhost", "localhost.localdomain", "127.0.0.1", "::1", "0.0.0.0"):
        raise ValueError(f"Access to local host '{hostname}' is prohibited (SSRF protection).")

    # If hostname is an IP literal
    try:
        ip = ipaddress.ip_address(hostname)
        if not is_safe_ip(str(ip)):
            raise ValueError(
                f"Access to private/reserved IP address '{hostname}' is prohibited (SSRF protection)."
            )
        return clean_url
    except ValueError:
        pass  # It's a domain name, proceed to DNS resolution

    # Resolve domain to IP addresses
    try:
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise ValueError(f"Could not resolve domain '{hostname}': {str(e)}")

    if not addr_info:
        raise ValueError(f"No IP addresses resolved for domain '{hostname}'.")

    for family, _, _, _, sockaddr in addr_info:
        ip_address = sockaddr[0]
        if not is_safe_ip(ip_address):
            raise ValueError(
                f"Domain '{hostname}' resolves to restricted IP '{ip_address}' (SSRF protection)."
            )

    return clean_url


def extract_cta_links(message: str) -> List[str]:
    """Finds all HTTP/HTTPS links in a message text.

    Args:
        message: Input string.

    Returns:
        List of URL strings found in the message.
    """
    matches = URL_REGEX.findall(message)
    # Clean trailing punctuation often attached to URLs in prose (.,!?:;)
    cleaned_urls = []
    for match in matches:
        clean = re.sub(r"[.,!?:;]+$", "", match)
        cleaned_urls.append(clean)
    return cleaned_urls


def validate_posting_message(message: str) -> Tuple[str, str]:
    """Validates the posting message per business rules.

    Rules:
    - Message length <= 200 characters.
    - Exactly one CTA link must be included.
    - The CTA link must be a valid HTTP/HTTPS URL.

    Args:
        message: Input message to be posted.

    Returns:
        Tuple of (cleaned_message, cta_url).

    Raises:
        ValueError: If validation fails.
    """
    if not message or not isinstance(message, str):
        raise ValueError("Message cannot be empty.")

    cleaned_msg = message.strip()

    if len(cleaned_msg) > 200:
        raise ValueError(
            f"Message length ({len(cleaned_msg)} characters) exceeds the maximum allowed limit of 200 characters."
        )

    links = extract_cta_links(cleaned_msg)

    if len(links) == 0:
        raise ValueError("Message must include exactly one CTA link, but none was found.")

    if len(links) > 1:
        raise ValueError(
            f"Message must include exactly one CTA link, but {len(links)} links were found: {', '.join(links)}."
        )

    cta_url = validate_url_format(links[0])

    return cleaned_msg, cta_url
