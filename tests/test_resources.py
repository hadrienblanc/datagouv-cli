"""Tests for the resources API client."""

import pytest
import respx
from httpx import Response

from cli_gouv.api.resources import ResourcesClient, ResourceDownloadError


class TestResourcesClient:
    """Tests for ResourcesClient class."""

    @pytest.fixture
    def mock_tabular_response(self) -> dict:
        """Sample tabular API response."""
        return {
            "data": [
                {"code_postal": "75001", "population": 1000},
                {"code_postal": "75002", "population": 2000},
            ],
            "meta": {
                "page": 1,
                "page_size": 20,
                "total": 2,
            },
            "schema": {
                "fields": [
                    {"name": "code_postal", "type": "string"},
                    {"name": "population", "type": "integer"},
                ]
            },
        }

    @pytest.mark.asyncio
    async def test_query_tabular(
        self, mock_tabular_response: dict
    ) -> None:
        """Test querying tabular data."""
        async with ResourcesClient() as client:
            with respx.mock:
                respx.get(
                    "https://tabular-api.data.gouv.fr/api/v1/resources/resource-1/data/"
                ).mock(
                    return_value=Response(200, json=mock_tabular_response)
                )
                result = await client.query_tabular(
                    "resource-1",
                    query="code_postal = '75001'",
                )
                assert len(result["data"]) == 2
                assert result["data"][0]["code_postal"] == "75001"

    @pytest.mark.asyncio
    async def test_query_tabular_with_pagination(
        self, mock_tabular_response: dict
    ) -> None:
        """Test tabular query with pagination parameters."""
        async with ResourcesClient() as client:
            with respx.mock:
                route = respx.get(
                    "https://tabular-api.data.gouv.fr/api/v1/resources/resource-1/data/"
                ).mock(
                    return_value=Response(200, json=mock_tabular_response)
                )
                await client.query_tabular(
                    "resource-1",
                    page=2,
                    page_size=50,
                )
                request = route.calls.last.request
                assert "page=2" in str(request.url)
                assert "page_size=50" in str(request.url)

    @pytest.mark.asyncio
    async def test_query_tabular_with_columns(
        self, mock_tabular_response: dict
    ) -> None:
        """Test that with_columns parameter is passed."""
        async with ResourcesClient() as client:
            with respx.mock:
                route = respx.get(
                    "https://tabular-api.data.gouv.fr/api/v1/resources/resource-1/data/"
                ).mock(
                    return_value=Response(200, json=mock_tabular_response)
                )
                await client.query_tabular("resource-1", with_columns=True)
                request = route.calls.last.request
                assert "with_columns=true" in str(request.url)

    @pytest.mark.asyncio
    async def test_query_tabular_page_validation(self) -> None:
        """Test that page must be >= 1."""
        async with ResourcesClient() as client:
            with pytest.raises(ValueError, match="page must be >= 1"):
                await client.query_tabular("resource-1", page=0)

    @pytest.mark.asyncio
    async def test_query_tabular_page_size_validation(self) -> None:
        """Test that page_size must be >= 1."""
        async with ResourcesClient() as client:
            with pytest.raises(ValueError, match="page_size must be >= 1"):
                await client.query_tabular("resource-1", page_size=0)

    @pytest.mark.asyncio
    async def test_get_schema(self) -> None:
        """Test getting resource schema."""
        schema = {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        }
        async with ResourcesClient() as client:
            with respx.mock:
                respx.get(
                    "https://tabular-api.data.gouv.fr/api/v1/resources/resource-1/schema/"
                ).mock(
                    return_value=Response(200, json=schema)
                )
                result = await client.get_schema("resource-1")
                assert len(result["fields"]) == 2

    @pytest.mark.asyncio
    async def test_download(self) -> None:
        """Test downloading resource content."""
        async with ResourcesClient() as client:
            with respx.mock:
                respx.get("https://example.com/data.csv").mock(
                    return_value=Response(200, content=b"id,name\n1,test")
                )
                content = await client.download("https://example.com/data.csv")
                assert content == b"id,name\n1,test"

    @pytest.mark.asyncio
    async def test_download_404(self) -> None:
        """Test download 404 handling."""
        async with ResourcesClient() as client:
            with respx.mock:
                respx.get("https://example.com/notfound.csv").mock(
                    return_value=Response(404, text="Not found")
                )
                with pytest.raises(ResourceDownloadError, match="not found"):
                    await client.download("https://example.com/notfound.csv")

    @pytest.mark.asyncio
    async def test_download_500(self) -> None:
        """Test download server error handling."""
        async with ResourcesClient() as client:
            with respx.mock:
                respx.get("https://example.com/error.csv").mock(
                    return_value=Response(500, text="Internal error")
                )
                with pytest.raises(ResourceDownloadError, match="Failed to download"):
                    await client.download("https://example.com/error.csv")

    @pytest.mark.asyncio
    async def test_download_rejects_http_url(self) -> None:
        """Test that non-HTTPS URLs are rejected."""
        async with ResourcesClient() as client:
            with pytest.raises(ValueError, match="not allowed"):
                await client.download("http://example.com/data.csv")

    @pytest.mark.asyncio
    async def test_download_rejects_file_url(self) -> None:
        """Test that file:// URLs are rejected."""
        async with ResourcesClient() as client:
            with pytest.raises(ValueError, match="not allowed"):
                await client.download("file:///etc/passwd")
