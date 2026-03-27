"""Resources API client for data.gouv.fr."""

from typing import Any

from cli_gouv.api.client import BaseClient, DataGouvAPIError


class ResourceDownloadError(DataGouvAPIError):
    """Error downloading a resource."""

    pass


class ResourcesClient(BaseClient):
    """Client for resources API endpoints.

    Note: Resources on data.gouv.fr are accessed via their parent dataset.
    Use DatasetsClient.get_dataset() to get resources, or use query_tabular()
    for tabular data.
    """

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
            query: SQL-like query string (WHERE clause). Passed as-is to the
                Tabular API which handles validation. Not sanitized client-side.
            page: Page number (1-indexed, min 1).
            page_size: Number of rows per page (max 200, min 1).
            with_columns: Include column information in response.

        Returns:
            Query results with data rows and pagination info.

        Raises:
            ValueError: If page or page_size are out of bounds.
        """
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1:
            raise ValueError("page_size must be >= 1")

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

    async def download(self, url: str) -> bytes:
        """Download a resource from its URL.

        Args:
            url: Direct download URL for the resource (HTTPS only).

        Returns:
            Raw file content as bytes.

        Raises:
            ValueError: If URL scheme is not HTTPS.
            ResourceDownloadError: If download fails.
        """
        self.validate_url(url)
        client = self._get_client()

        try:
            response = await client.get(url)

            if response.status_code == 404:
                raise ResourceDownloadError(
                    f"Resource not found: {url}",
                    status_code=404,
                )
            if response.status_code != 200:
                raise ResourceDownloadError(
                    f"Failed to download resource: HTTP {response.status_code}",
                    status_code=response.status_code,
                )

            return response.content

        except Exception as e:
            if isinstance(e, ResourceDownloadError):
                raise
            raise ResourceDownloadError(f"Download failed: {e}") from e
