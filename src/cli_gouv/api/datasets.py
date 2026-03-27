"""Datasets API client for data.gouv.fr."""

from typing import Any

from cli_gouv.api.client import BaseClient


class DatasetsClient(BaseClient):
    """Client for datasets API endpoints."""

    async def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
        organization: str | None = None,
        tag: str | None = None,
        sort: str | None = None,
    ) -> dict[str, Any]:
        """Search for datasets.

        Args:
            query: Search query string.
            page: Page number (1-indexed, min 1).
            page_size: Number of results per page (max 100, min 1).
            organization: Filter by organization ID or name.
            tag: Filter by tag.
            sort: Sort field (e.g., '-created', 'title').

        Returns:
            Search results with pagination info.

        Raises:
            ValueError: If page or page_size are out of bounds.
        """
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1:
            raise ValueError("page_size must be >= 1")

        params: dict[str, Any] = {
            "q": query,
            "page": page,
            "page_size": min(page_size, 100),
        }

        if organization:
            params["organization"] = organization
        if tag:
            params["tag"] = tag
        if sort:
            params["sort"] = sort

        return await self._get(self.MAIN_API_URL, "/datasets/", params=params)

    async def get_dataset(self, dataset_id: str) -> dict[str, Any]:
        """Get detailed information about a dataset.

        Args:
            dataset_id: Dataset ID or slug.

        Returns:
            Dataset details including metadata and resources.
        """
        return await self._get(self.MAIN_API_URL, f"/datasets/{dataset_id}/")

    async def list_resources(self, dataset_id: str) -> list[dict[str, Any]]:
        """List all resources in a dataset.

        Args:
            dataset_id: Dataset ID or slug.

        Returns:
            List of resources with metadata.
        """
        dataset = await self.get_dataset(dataset_id)
        return dataset.get("resources", [])

    async def get_metrics(self, dataset_id: str) -> dict[str, Any]:
        """Get metrics (views, downloads) for a dataset.

        Args:
            dataset_id: Dataset ID.

        Returns:
            Metrics data with monthly statistics.
        """
        return await self._get(
            self.METRICS_API_URL,
            f"/datasets/{dataset_id}/",
        )
