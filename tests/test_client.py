"""Tests for the base API client."""

import pytest
import respx
from httpx import Response

from cli_gouv.api.client import (
    BaseClient,
    DataGouvAPIError,
    JSONParseError,
    NotFoundError,
    RateLimitError,
    ServerError,
)


class TestBaseClient:
    """Tests for BaseClient class."""

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test async context manager initialization."""
        async with BaseClient() as client:
            assert client._client is not None

    @pytest.mark.asyncio
    async def test_context_manager_cleanup(self) -> None:
        """Test that client is cleaned up on exit."""
        client = BaseClient()
        async with client:
            pass
        assert client._client is None

    @pytest.mark.asyncio
    async def test_get_client_outside_context(self) -> None:
        """Test that _get_client raises outside context."""
        client = BaseClient()
        with pytest.raises(RuntimeError, match="not initialized"):
            client._get_client()

    @pytest.mark.asyncio
    async def test_successful_get_request(self) -> None:
        """Test successful GET request."""
        async with BaseClient() as client:
            with respx.mock:
                respx.get("https://example.com/api/test").mock(
                    return_value=Response(200, json={"success": True})
                )
                result = await client._get("https://example.com", "/api/test")
                assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_404_not_found(self) -> None:
        """Test 404 response handling."""
        async with BaseClient() as client:
            with respx.mock:
                respx.get("https://example.com/api/notfound").mock(
                    return_value=Response(404, text="Not found")
                )
                with pytest.raises(NotFoundError):
                    await client._get("https://example.com", "/api/notfound")

    @pytest.mark.asyncio
    async def test_429_rate_limit(self) -> None:
        """Test rate limit handling."""
        async with BaseClient() as client:
            with respx.mock:
                respx.get("https://example.com/api/rate-limited").mock(
                    return_value=Response(429, text="Too many requests")
                )
                with pytest.raises(RateLimitError):
                    await client._get("https://example.com", "/api/rate-limited")

    @pytest.mark.asyncio
    async def test_500_server_error(self) -> None:
        """Test server error handling."""
        async with BaseClient() as client:
            with respx.mock:
                respx.get("https://example.com/api/error").mock(
                    return_value=Response(500, text="Internal server error")
                )
                with pytest.raises(ServerError):
                    await client._get("https://example.com", "/api/error")

    @pytest.mark.asyncio
    async def test_400_bad_request(self) -> None:
        """Test generic 400 error handling."""
        async with BaseClient() as client:
            with respx.mock:
                respx.get("https://example.com/api/bad").mock(
                    return_value=Response(400, text="Bad request")
                )
                with pytest.raises(DataGouvAPIError, match="400"):
                    await client._get("https://example.com", "/api/bad")

    @pytest.mark.asyncio
    async def test_url_construction(self) -> None:
        """Test URL construction with trailing/leading slashes."""
        async with BaseClient() as client:
            with respx.mock:
                # The URL becomes https://example.com/api/v1/test/ (trailing slash preserved)
                route = respx.get("https://example.com/api/v1/test/").mock(
                    return_value=Response(200, json={"ok": True})
                )
                result = await client._get("https://example.com/", "/api/v1/test/")
                assert result == {"ok": True}
                # Verify the request was made
                assert route.called

    @pytest.mark.asyncio
    async def test_json_parse_error(self) -> None:
        """Test JSON parsing error handling."""
        async with BaseClient() as client:
            with respx.mock:
                respx.get("https://example.com/api/invalid-json").mock(
                    return_value=Response(200, text="Not valid JSON {{{")
                )
                with pytest.raises(JSONParseError, match="Failed to parse JSON"):
                    await client._get("https://example.com", "/api/invalid-json")
