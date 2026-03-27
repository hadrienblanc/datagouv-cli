"""Dataservices API client for data.gouv.fr."""

from typing import Any

from cli_gouv.api.client import BaseClient


class DataservicesClient(BaseClient):
    """Client for dataservices (external APIs) endpoints."""

    async def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
        organization: str | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """Search for dataservices (external APIs).

        Args:
            query: Search query string.
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).
            organization: Filter by organization ID or name.
            tag: Filter by tag.

        Returns:
            Search results with pagination info.
        """
        params: dict[str, Any] = {
            "q": query,
            "page": page,
            "page_size": min(page_size, 100),
        }

        if organization:
            params["organization"] = organization
        if tag:
            params["tag"] = tag

        return await self._get(self.MAIN_API_URL, "/dataservices/", params=params)

    async def get_dataservice(self, dataservice_id: str) -> dict[str, Any]:
        """Get detailed information about a dataservice.

        Args:
            dataservice_id: Dataservice ID.

        Returns:
            Dataservice details including API URL, description.
        """
        return await self._get(
            self.MAIN_API_URL,
            f"/dataservices/{dataservice_id}/",
        )

    async def get_openapi_spec(self, dataservice_id: str) -> dict[str, Any]:
        """Get the OpenAPI specification for a dataservice.

        Args:
            dataservice_id: Dataservice ID.

        Returns:
            OpenAPI specification summary with endpoints.

        Raises:
            ValueError: If dataservice has no OpenAPI URL.
        """
        dataservice = await self.get_dataservice(dataservice_id)
        openapi_url = dataservice.get("openapi_url")

        if not openapi_url:
            raise ValueError(f"No OpenAPI URL for dataservice {dataservice_id}")

        # Fetch the OpenAPI spec directly
        client = self._get_client()
        response = await client.get(openapi_url)

        if response.status_code != 200:
            raise ValueError(f"Failed to fetch OpenAPI spec: HTTP {response.status_code}")

        return response.json()
