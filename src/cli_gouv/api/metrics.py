"""Metrics API client for data.gouv.fr."""

from typing import Any

from cli_gouv.api.client import BaseClient


class MetricsClient(BaseClient):
    """Client for metrics API endpoints."""

    async def get_dataset_metrics(
        self,
        dataset_id: str,
        limit: int = 12,
    ) -> dict[str, Any]:
        """Get metrics (views, downloads) for a dataset.

        Args:
            dataset_id: Dataset ID.
            limit: Number of months to return (max 100).

        Returns:
            Monthly metrics with views and downloads.
        """
        return await self._get(
            self.METRICS_API_URL,
            f"/datasets/{dataset_id}/",
            params={"limit": min(limit, 100)},
        )

    async def get_resource_metrics(
        self,
        resource_id: str,
        limit: int = 12,
    ) -> dict[str, Any]:
        """Get metrics (downloads) for a resource.

        Args:
            resource_id: Resource ID.
            limit: Number of months to return (max 100).

        Returns:
            Monthly metrics with downloads.
        """
        return await self._get(
            self.METRICS_API_URL,
            f"/resources/{resource_id}/",
            params={"limit": min(limit, 100)},
        )

    async def get_combined_metrics(
        self,
        dataset_id: str | None = None,
        resource_id: str | None = None,
        limit: int = 12,
    ) -> dict[str, Any]:
        """Get metrics for dataset and/or resource.

        Args:
            dataset_id: Dataset ID (optional).
            resource_id: Resource ID (optional).
            limit: Number of months to return.

        Returns:
            Combined metrics data.

        Raises:
            ValueError: If neither dataset_id nor resource_id is provided.
        """
        if not dataset_id and not resource_id:
            raise ValueError("Either dataset_id or resource_id must be provided")

        result: dict[str, Any] = {}

        if dataset_id:
            result["dataset"] = await self.get_dataset_metrics(dataset_id, limit)

        if resource_id:
            result["resource"] = await self.get_resource_metrics(resource_id, limit)

        return result
