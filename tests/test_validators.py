"""Unit tests for URL validation, SSRF defense, and posting message constraints."""

import pytest
from app.utils.validators import (
    extract_cta_links,
    is_safe_ip,
    validate_posting_message,
    validate_ssrf_safe_url,
    validate_url_format,
)


class TestUrlValidators:
    """Tests URL validation and SSRF defenses."""

    def test_validate_url_format_valid(self):
        url = "https://example.com/about?tab=services"
        assert validate_url_format(url) == "https://example.com/about?tab=services"

    def test_validate_url_format_invalid_scheme(self):
        with pytest.raises(ValueError, match="Only 'http' and 'https' are supported"):
            validate_url_format("ftp://example.com/file.txt")

    def test_validate_url_format_file_scheme(self):
        with pytest.raises(ValueError, match="Only 'http' and 'https' are supported"):
            validate_url_format("file:///etc/passwd")

    def test_validate_url_format_embedded_credentials(self):
        with pytest.raises(ValueError, match="embedded user credentials are not allowed"):
            validate_url_format("http://admin:secret@example.com")

    def test_is_safe_ip_public(self):
        # Public DNS IP
        assert is_safe_ip("8.8.8.8") is True
        assert is_safe_ip("1.1.1.1") is True

    def test_is_safe_ip_private_and_loopback(self):
        assert is_safe_ip("127.0.0.1") is False
        assert is_safe_ip("10.0.0.1") is False
        assert is_safe_ip("192.168.1.1") is False
        assert is_safe_ip("172.16.0.5") is False
        assert is_safe_ip("169.254.169.254") is False  # AWS metadata service IP
        assert is_safe_ip("::1") is False

    def test_validate_ssrf_safe_url_blocks_localhost(self):
        with pytest.raises(ValueError, match="SSRF protection"):
            validate_ssrf_safe_url("http://localhost:8000")

    def test_validate_ssrf_safe_url_blocks_loopback_ip(self):
        with pytest.raises(ValueError, match="SSRF protection"):
            validate_ssrf_safe_url("http://127.0.0.1/admin")

    def test_validate_ssrf_safe_url_blocks_private_ip(self):
        with pytest.raises(ValueError, match="SSRF protection"):
            validate_ssrf_safe_url("http://192.168.1.50/dashboard")


class TestPostingMessageValidation:
    """Tests business rules for the multi-platform posting endpoint."""

    def test_valid_message_with_cta(self):
        msg = "Grow your business online today with our top-rated platform! https://example.com"
        cleaned_msg, cta = validate_posting_message(msg)
        assert cleaned_msg == msg
        assert cta == "https://example.com"

    def test_message_exceeds_200_chars(self):
        long_text = "A" * 190 + " https://example.com"
        assert len(long_text) > 200
        with pytest.raises(ValueError, match="exceeds the maximum allowed limit of 200 characters"):
            validate_posting_message(long_text)

    def test_message_without_cta(self):
        msg = "Great platform with no links included in the text."
        with pytest.raises(ValueError, match="Message must include exactly one CTA link, but none was found"):
            validate_posting_message(msg)

    def test_message_with_multiple_cta_links(self):
        msg = "Visit https://first.com and also check out https://second.com"
        with pytest.raises(ValueError, match="Message must include exactly one CTA link, but 2 links were found"):
            validate_posting_message(msg)

    def test_extract_cta_links(self):
        text = "Check https://example.com/test, and join us!"
        links = extract_cta_links(text)
        assert len(links) == 1
        assert links[0] == "https://example.com/test"
