"""Tests for the dataservices API client."""

import pytest
import respx
from httpx import Response

from cli_gouv.api.dataservices import DataservicesClient, OpenAPIFetchError


class TestDataservicesClient:
    """Tests for DataservicesClient class."""

    @pytest.fixture
    def mock_search_response(self) -> dict:
        """Sample search response."""
        return {
            "data": [
                {
                    "id": "ds-1",
                    "title": "API Adresse",
                    "description": "API de géocodage",
                    "base_api_url": "https://api-adresse.fr/",
                    "organization": {"name": "Base Adresse Nationale"},
                    "tags": ["adresse", "geocodage"],
                }
            ],
            "next_page": None,
            "page": 1,
            "pagesize": 20,
            "total": 1,
        }

    @pytest.fixture
    def mock_dataservice_response(self) -> dict:
        """Sample dataservice detail response."""
        return {
            "id": "ds-1",
            "title": "API Adresse",
            "description": "API de géocodage français",
            "base_api_url": "https://api-adresse.fr/",
            "openapi_url": "https://api-adresse.fr/swagger.json",
            "organization": {
                "name": "Base Adresse Nationale",
                "id": "ban",
            },
            "tags": ["adresse", "geocodage"],
            "license": "Licence Ouverte",
            "created_at": "2024-01-01T00:00:00",
            "last_modified": "2024-06-01T00:00:00",
        }

    @pytest.fixture
    def mock_openapi_spec(self) -> dict:
        """Sample OpenAPI spec."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "API Adresse",
                "version": "1.0.0",
            },
            "paths": {
                "/search": {
                    "get": {
                        "summary": "Rechercher une adresse",
                        "parameters": [
                            {
                                "name": "q",
                                "in": "query",
                                "required": True,
                                "description": "Adresse à rechercher",
                            }
                        ],
                    }
                }
            },
        }

    @pytest.mark.asyncio
    async def test_search_dataservices(
        self, mock_search_response: dict
    ) -> None:
        """Test dataservice search."""
        async with DataservicesClient() as client:
            with respx.mock:
                respx.get("https://www.data.gouv.fr/api/1/dataservices/").mock(
                    return_value=Response(200, json=mock_search_response)
                )
                result = await client.search("adresse")
                assert result["total"] == 1
                assert result["data"][0]["title"] == "API Adresse"

    @pytest.mark.asyncio
    async def test_search_with_filters(
        self, mock_search_response: dict
    ) -> None:
        """Test dataservice search with filters."""
        async with DataservicesClient() as client:
            with respx.mock:
                route = respx.get("https://www.data.gouv.fr/api/1/dataservices/").mock(
                    return_value=Response(200, json=mock_search_response)
                )
                await client.search(
                    "adresse",
                    organization="ban",
                    tag="geocodage",
                )
                request = route.calls.last.request
                assert "organization=ban" in str(request.url)
                assert "tag=geocodage" in str(request.url)

    @pytest.mark.asyncio
    async def test_search_page_validation(self) -> None:
        """Test that page must be >= 1."""
        async with DataservicesClient() as client:
            with pytest.raises(ValueError, match="page must be >= 1"):
                await client.search("test", page=0)

    @pytest.mark.asyncio
    async def test_search_page_size_validation(self) -> None:
        """Test that page_size must be >= 1."""
        async with DataservicesClient() as client:
            with pytest.raises(ValueError, match="page_size must be >= 1"):
                await client.search("test", page_size=0)

    @pytest.mark.asyncio
    async def test_get_dataservice(
        self, mock_dataservice_response: dict
    ) -> None:
        """Test getting a single dataservice."""
        async with DataservicesClient() as client:
            with respx.mock:
                respx.get("https://www.data.gouv.fr/api/1/dataservices/ds-1/").mock(
                    return_value=Response(200, json=mock_dataservice_response)
                )
                result = await client.get_dataservice("ds-1")
                assert result["id"] == "ds-1"
                assert result["base_api_url"] == "https://api-adresse.fr/"

    @pytest.mark.asyncio
    async def test_get_openapi_spec(
        self,
        mock_dataservice_response: dict,
        mock_openapi_spec: dict,
    ) -> None:
        """Test getting OpenAPI spec for a dataservice."""
        async with DataservicesClient() as client:
            with respx.mock:
                respx.get("https://www.data.gouv.fr/api/1/dataservices/ds-1/").mock(
                    return_value=Response(200, json=mock_dataservice_response)
                )
                respx.get("https://api-adresse.fr/swagger.json").mock(
                    return_value=Response(200, json=mock_openapi_spec)
                )
                result = await client.get_openapi_spec("ds-1")
                assert result["info"]["title"] == "API Adresse"
                assert "/search" in result["paths"]

    @pytest.mark.asyncio
    async def test_get_openapi_spec_no_url(
        self, mock_dataservice_response: dict
    ) -> None:
        """Test OpenAPI spec fails when no URL available."""
        # Modify response to remove openapi_url
        response = mock_dataservice_response.copy()
        response["openapi_url"] = None

        async with DataservicesClient() as client:
            with respx.mock:
                respx.get("https://www.data.gouv.fr/api/1/dataservices/ds-1/").mock(
                    return_value=Response(200, json=response)
                )
                with pytest.raises(ValueError, match="No OpenAPI URL"):
                    await client.get_openapi_spec("ds-1")

    @pytest.mark.asyncio
    async def test_get_openapi_spec_fetch_error(
        self,
        mock_dataservice_response: dict,
    ) -> None:
        """Test OpenAPI spec fetch error handling."""
        async with DataservicesClient() as client:
            with respx.mock:
                respx.get("https://www.data.gouv.fr/api/1/dataservices/ds-1/").mock(
                    return_value=Response(200, json=mock_dataservice_response)
                )
                respx.get("https://api-adresse.fr/swagger.json").mock(
                    return_value=Response(500, text="Internal error")
                )
                with pytest.raises(OpenAPIFetchError, match="Failed to fetch"):
                    await client.get_openapi_spec("ds-1")

    @pytest.mark.asyncio
    async def test_get_openapi_spec_not_found(
        self,
        mock_dataservice_response: dict,
    ) -> None:
        """Test OpenAPI spec 404 handling."""
        async with DataservicesClient() as client:
            with respx.mock:
                respx.get("https://www.data.gouv.fr/api/1/dataservices/ds-1/").mock(
                    return_value=Response(200, json=mock_dataservice_response)
                )
                respx.get("https://api-adresse.fr/swagger.json").mock(
                    return_value=Response(404, text="Not found")
                )
                with pytest.raises(OpenAPIFetchError, match="not found"):
                    await client.get_openapi_spec("ds-1")

    @pytest.mark.asyncio
    async def test_get_openapi_spec_rejects_http_url(self) -> None:
        """Test that non-HTTPS OpenAPI URLs are rejected."""
        response = {
            "id": "ds-1",
            "openapi_url": "http://insecure.example.com/spec.json",
        }
        async with DataservicesClient() as client:
            with respx.mock:
                respx.get("https://www.data.gouv.fr/api/1/dataservices/ds-1/").mock(
                    return_value=Response(200, json=response)
                )
                with pytest.raises(ValueError, match="not allowed"):
                    await client.get_openapi_spec("ds-1")
