"""Resources API client for data.gouv.fr."""

from typing import Any

from cli_gouv.api.client import BaseClient


class ResourcesClient(BaseClient):
    """Client for resources API endpoints."""

    async def get_resource(self, resource_id: str) -> dict[str, Any]:
        """Get detailed information about a resource.

        Args:
            resource_id: Resource ID.

        Returns:
            Resource details including format, size, URL.
        """
        # Note: Resources are accessed via the datasets endpoint
        # This is a simplified version - in practice you'd need the dataset_id too
        return await self._get(
            self.MAIN_API_URL,
            f"/datasets/undefined/resources/{resource_id}/",
        )

    async def download(self, resource_id: str) -> bytes:
        """Download a resource's file content.

        Args:
            resource_id: Resource ID.

        Returns:
            Raw file content as bytes.

        Raises:
            ValueError: If resource has no download URL.
        """
        resource = await self.get_resource(resource_id)
        url = resource.get("url")

        if not url:
            raise ValueError(f"No download URL for resource {resource_id}")

        client = self._get_client()
        response = await client.get(url)

        if response.status_code != 200:
            raise ValueError(f"Failed to download resource: HTTP {response.status_code}")

        return response.content

    async def query_tabular(
        self,
        resource_id: str,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
        with_columns: bool = True,
    ) -> dict[str, Any]:
        """Query tabular data via the Tabular API.

        Args:
            resource_id: Resource ID (must be CSV or XLS).
            query: SQL-like query string (WHERE clause).
            page: Page number (1-indexed).
            page_size: Number of rows per page (max 200).
            with_columns: Include column information in response.

        Returns:
            Query results with data rows and pagination info.
        """
        params: dict[str, Any] = {
            "page": page,
            "page_size": min(page_size, 200),
            "with_columns": str(with_columns).lower(),
        }

        if query:
            params["where"] = query

        return await self._get(
            self.TABULAR_API_URL,
            f"/resources/{resource_id}/data/",
            params=params,
        )

    async def get_schema(self, resource_id: str) -> dict[str, Any]:
        """Get the schema (column info) for a tabular resource.

        Args:
            resource_id: Resource ID.

        Returns:
            Schema information including column names and types.
        """
        return await self._get(
            self.TABULAR_API_URL,
            f"/resources/{resource_id}/schema/",
        )
