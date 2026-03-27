"""Dataservices API client for data.gouv.fr."""

from typing import Any

from cli_gouv.api.client import BaseClient, DataGouvAPIError


class OpenAPIFetchError(DataGouvAPIError):
    """Error fetching OpenAPI specification."""

    pass


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
            page: Page number (1-indexed, min 1).
            page_size: Number of results per page (max 100, min 1).
            organization: Filter by organization ID or name.
            tag: Filter by tag.

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
            OpenAPIFetchError: If fetching the spec fails.
        """
        dataservice = await self.get_dataservice(dataservice_id)
        openapi_url = dataservice.get("openapi_url")

        if not openapi_url:
            raise ValueError(f"No OpenAPI URL for dataservice {dataservice_id}")

        self.validate_url(openapi_url)

        # Fetch the OpenAPI spec directly from external URL
        client = self._get_client()

        try:
            response = await client.get(openapi_url, follow_redirects=True)

            if response.status_code == 404:
                raise OpenAPIFetchError(
                    f"OpenAPI spec not found: {openapi_url}",
                    status_code=404,
                )
            if response.status_code != 200:
                raise OpenAPIFetchError(
                    f"Failed to fetch OpenAPI spec: HTTP {response.status_code}",
                    status_code=response.status_code,
                )

            try:
                return response.json()
            except ValueError as e:
                raise OpenAPIFetchError(
                    f"Invalid JSON in OpenAPI spec: {e}",
                    status_code=200,
                ) from e

        except OpenAPIFetchError:
            raise
        except Exception as e:
            raise OpenAPIFetchError(f"Failed to fetch OpenAPI spec: {e}") from e
