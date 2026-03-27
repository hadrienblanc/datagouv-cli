"""Tests for the resources API client."""

import pytest
import respx
from httpx import Response

from cli_gouv.api.resources import ResourcesClient


class TestResourcesClient:
    """Tests for ResourcesClient class."""

    @pytest.fixture
    def mock_resource_response(self) -> dict:
        """Sample resource detail response."""
        return {
            "id": "resource-1",
            "title": "Population CSV",
            "description": "Données de population au format CSV",
            "format": "csv",
            "mime": "text/csv",
            "filesize": 1024000,
            "url": "https://example.com/population.csv",
            "checksum": {"type": "sha256", "value": "abc123"},
            "created_at": "2024-01-01T00:00:00",
            "last_modified": "2024-06-01T00:00:00",
        }

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
