"""Tests for the metrics API client."""

import pytest
import respx
from httpx import Response

from datagouv_cli.api.metrics import MetricsClient


class TestMetricsClient:
    """Tests for MetricsClient class."""

    @pytest.fixture
    def mock_dataset_metrics(self) -> dict:
        """Sample dataset metrics response."""
        return {
            "dataset_id": "dataset-1",
            "metrics": [
                {
                    "month": "2024-06",
                    "views": 1500,
                    "downloads": 300,
                },
                {
                    "month": "2024-05",
                    "views": 1200,
                    "downloads": 250,
                },
            ],
        }

    @pytest.fixture
    def mock_resource_metrics(self) -> dict:
        """Sample resource metrics response."""
        return {
            "resource_id": "resource-1",
            "metrics": [
                {
                    "month": "2024-06",
                    "downloads": 150,
                },
                {
                    "month": "2024-05",
                    "downloads": 120,
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_get_dataset_metrics(
        self, mock_dataset_metrics: dict
    ) -> None:
        """Test getting dataset metrics."""
        async with MetricsClient() as client:
            with respx.mock:
                respx.get("https://stats.data.gouv.fr/api/v1/datasets/dataset-1/").mock(
                    return_value=Response(200, json=mock_dataset_metrics)
                )
                result = await client.get_dataset_metrics("dataset-1")
                assert result["dataset_id"] == "dataset-1"
                assert len(result["metrics"]) == 2

    @pytest.mark.asyncio
    async def test_get_dataset_metrics_with_limit(
        self, mock_dataset_metrics: dict
    ) -> None:
        """Test dataset metrics with limit parameter."""
        async with MetricsClient() as client:
            with respx.mock:
                route = respx.get(
                    "https://stats.data.gouv.fr/api/v1/datasets/dataset-1/"
                ).mock(
                    return_value=Response(200, json=mock_dataset_metrics)
                )
                await client.get_dataset_metrics("dataset-1", limit=24)
                request = route.calls.last.request
                assert "limit=24" in str(request.url)

    @pytest.mark.asyncio
    async def test_get_dataset_metrics_limit_capped(
        self, mock_dataset_metrics: dict
    ) -> None:
        """Test that metrics limit is capped at 100."""
        async with MetricsClient() as client:
            with respx.mock:
                route = respx.get(
                    "https://stats.data.gouv.fr/api/v1/datasets/dataset-1/"
                ).mock(
                    return_value=Response(200, json=mock_dataset_metrics)
                )
                await client.get_dataset_metrics("dataset-1", limit=200)
                request = route.calls.last.request
                assert "limit=100" in str(request.url)

    @pytest.mark.asyncio
    async def test_get_resource_metrics(
        self, mock_resource_metrics: dict
    ) -> None:
        """Test getting resource metrics."""
        async with MetricsClient() as client:
            with respx.mock:
                respx.get(
                    "https://stats.data.gouv.fr/api/v1/resources/resource-1/"
                ).mock(
                    return_value=Response(200, json=mock_resource_metrics)
                )
                result = await client.get_resource_metrics("resource-1")
                assert result["resource_id"] == "resource-1"
                assert result["metrics"][0]["downloads"] == 150

    @pytest.mark.asyncio
    async def test_get_combined_metrics(
        self,
        mock_dataset_metrics: dict,
        mock_resource_metrics: dict,
    ) -> None:
        """Test getting combined metrics."""
        async with MetricsClient() as client:
            with respx.mock:
                respx.get("https://stats.data.gouv.fr/api/v1/datasets/dataset-1/").mock(
                    return_value=Response(200, json=mock_dataset_metrics)
                )
                respx.get(
                    "https://stats.data.gouv.fr/api/v1/resources/resource-1/"
                ).mock(
                    return_value=Response(200, json=mock_resource_metrics)
                )
                result = await client.get_combined_metrics(
                    dataset_id="dataset-1",
                    resource_id="resource-1",
                )
                assert "dataset" in result
                assert "resource" in result
                assert result["dataset"]["dataset_id"] == "dataset-1"
                assert result["resource"]["resource_id"] == "resource-1"

    @pytest.mark.asyncio
    async def test_get_combined_metrics_no_ids(self) -> None:
        """Test combined metrics raises error when no IDs provided."""
        async with MetricsClient() as client:
            with pytest.raises(ValueError, match="Either dataset_id or resource_id"):
                await client.get_combined_metrics()

    @pytest.mark.asyncio
    async def test_dataset_metrics_limit_validation(self) -> None:
        """Test that limit must be >= 1 for dataset metrics."""
        async with MetricsClient() as client:
            with pytest.raises(ValueError, match="limit must be >= 1"):
                await client.get_dataset_metrics("dataset-1", limit=0)

    @pytest.mark.asyncio
    async def test_resource_metrics_limit_validation(self) -> None:
        """Test that limit must be >= 1 for resource metrics."""
        async with MetricsClient() as client:
            with pytest.raises(ValueError, match="limit must be >= 1"):
                await client.get_resource_metrics("resource-1", limit=0)

    @pytest.mark.asyncio
    async def test_combined_metrics_limit_validation(self) -> None:
        """Test that limit must be >= 1 for combined metrics."""
        async with MetricsClient() as client:
            with pytest.raises(ValueError, match="limit must be >= 1"):
                await client.get_combined_metrics(dataset_id="dataset-1", limit=0)
