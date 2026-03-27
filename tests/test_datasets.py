"""Tests for the datasets API client."""

import pytest
import respx
from httpx import Response

from cli_gouv.api.client import NotFoundError
from cli_gouv.api.datasets import DatasetsClient


class TestDatasetsClient:
    """Tests for DatasetsClient class."""

    @pytest.fixture
    def mock_search_response(self) -> dict:
        """Sample search response."""
        return {
            "data": [
                {
                    "id": "dataset-1",
                    "title": "Population française",
                    "description": "Données de population",
                    "page": "https://www.data.gouv.fr/fr/datasets/dataset-1/",
                    "organization": {"name": "INSEE", "id": "insee"},
                    "tags": ["population", "demographie"],
                    "resources": [],
                }
            ],
            "next_page": None,
            "page": 1,
            "pagesize": 20,
            "total": 1,
        }

    @pytest.fixture
    def mock_dataset_response(self) -> dict:
        """Sample dataset detail response."""
        return {
            "id": "dataset-1",
            "title": "Population française",
            "description": "Données de population par commune",
            "page": "https://www.data.gouv.fr/fr/datasets/dataset-1/",
            "organization": {
                "name": "INSEE",
                "id": "insee",
                "logo": "https://example.com/logo.png",
            },
            "tags": ["population", "demographie"],
            "resources": [
                {
                    "id": "resource-1",
                    "title": "Population 2024",
                    "format": "csv",
                    "mime": "text/csv",
                    "filesize": 1024000,
                    "url": "https://example.com/population.csv",
                }
            ],
            "created_at": "2024-01-01T00:00:00",
            "last_modified": "2024-06-01T00:00:00",
            "license": "Licence Ouverte",
        }

    @pytest.mark.asyncio
    async def test_search_datasets(
        self, mock_search_response: dict
    ) -> None:
        """Test dataset search."""
        async with DatasetsClient() as client:
            with respx.mock:
                respx.get("https://www.data.gouv.fr/api/1/datasets/").mock(
                    return_value=Response(200, json=mock_search_response)
                )
                result = await client.search("population")
                assert result["total"] == 1
                assert result["data"][0]["title"] == "Population française"

    @pytest.mark.asyncio
    async def test_search_with_filters(
        self, mock_search_response: dict
    ) -> None:
        """Test dataset search with filters."""
        async with DatasetsClient() as client:
            with respx.mock:
                route = respx.get("https://www.data.gouv.fr/api/1/datasets/").mock(
                    return_value=Response(200, json=mock_search_response)
                )
                await client.search(
                    "population",
                    organization="INSEE",
                    tag="demographie",
                    sort="-created",
                )
                # Check that filters were passed
                request = route.calls.last.request
                assert "organization=INSEE" in str(request.url)
                assert "tag=demographie" in str(request.url)
                assert "sort=-created" in str(request.url)

    @pytest.mark.asyncio
    async def test_search_page_size_limit(
        self, mock_search_response: dict
    ) -> None:
        """Test that page_size is capped at 100."""
        async with DatasetsClient() as client:
            with respx.mock:
                route = respx.get("https://www.data.gouv.fr/api/1/datasets/").mock(
                    return_value=Response(200, json=mock_search_response)
                )
                await client.search("test", page_size=200)
                request = route.calls.last.request
                assert "page_size=100" in str(request.url)

    @pytest.mark.asyncio
    async def test_get_dataset(
        self, mock_dataset_response: dict
    ) -> None:
        """Test getting a single dataset."""
        async with DatasetsClient() as client:
            with respx.mock:
                respx.get("https://www.data.gouv.fr/api/1/datasets/dataset-1/").mock(
                    return_value=Response(200, json=mock_dataset_response)
                )
                result = await client.get_dataset("dataset-1")
                assert result["id"] == "dataset-1"
                assert len(result["resources"]) == 1

    @pytest.mark.asyncio
    async def test_get_dataset_not_found(self) -> None:
        """Test getting a non-existent dataset."""
        async with DatasetsClient() as client:
            with respx.mock:
                respx.get("https://www.data.gouv.fr/api/1/datasets/not-found/").mock(
                    return_value=Response(404, text="Not found")
                )
                with pytest.raises(NotFoundError):
                    await client.get_dataset("not-found")

    @pytest.mark.asyncio
    async def test_list_resources(
        self, mock_dataset_response: dict
    ) -> None:
        """Test listing resources from a dataset."""
        async with DatasetsClient() as client:
            with respx.mock:
                respx.get("https://www.data.gouv.fr/api/1/datasets/dataset-1/").mock(
                    return_value=Response(200, json=mock_dataset_response)
                )
                resources = await client.list_resources("dataset-1")
                assert len(resources) == 1
                assert resources[0]["format"] == "csv"
