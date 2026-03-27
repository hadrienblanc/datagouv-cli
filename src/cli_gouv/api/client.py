"""Base HTTP client for data.gouv.fr APIs."""

import json
from urllib.parse import urlparse
from typing import Any

import httpx

ALLOWED_URL_SCHEMES = ("https",)


class DataGouvAPIError(Exception):
    """Base exception for data.gouv.fr API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(DataGouvAPIError):
    """Resource not found (404)."""

    pass


class RateLimitError(DataGouvAPIError):
    """Rate limit exceeded (429)."""

    pass


class ServerError(DataGouvAPIError):
    """Server error (5xx)."""

    pass


class JSONParseError(DataGouvAPIError):
    """Error parsing JSON response."""

    pass


class BaseClient:
    """Base HTTP client with error handling.

    Note: This client does not implement automatic retries.
    For production use, consider adding retry logic with exponential backoff.
    """

    # API endpoints
    MAIN_API_URL = "https://www.data.gouv.fr/api/1"
    TABULAR_API_URL = "https://tabular-api.data.gouv.fr/api/v1"
    METRICS_API_URL = "https://stats.data.gouv.fr/api/v1"

    def __init__(self, timeout: float = 30.0) -> None:
        """Initialize the HTTP client.

        Args:
            timeout: Request timeout in seconds.
        """
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "BaseClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get the HTTP client, raising if not initialized."""
        if self._client is None:
            raise RuntimeError("Client not initialized. Use async with.")
        return self._client

    async def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to request.
            params: Query parameters.

        Returns:
            Parsed JSON response.

        Raises:
            NotFoundError: Resource not found.
            RateLimitError: Rate limit exceeded.
            ServerError: Server error.
            JSONParseError: Failed to parse JSON response.
            DataGouvAPIError: Other API errors.
        """
        client = self._get_client()

        try:
            response = await client.request(method, url, params=params)

            # Handle HTTP errors
            if response.status_code == 404:
                raise NotFoundError(
                    f"Resource not found: {url}",
                    status_code=404,
                )
            if response.status_code == 429:
                raise RateLimitError(
                    "Rate limit exceeded. Please wait before retrying.",
                    status_code=429,
                )
            if response.status_code >= 500:
                raise ServerError(
                    f"Server error ({response.status_code}): {response.text[:200]}",
                    status_code=response.status_code,
                )
            if response.status_code >= 400:
                raise DataGouvAPIError(
                    f"API error ({response.status_code}): {response.text[:200]}",
                    status_code=response.status_code,
                )

            # Parse JSON with error handling
            try:
                return response.json()
            except json.JSONDecodeError as e:
                raise JSONParseError(
                    f"Failed to parse JSON response from {url}: {e}",
                ) from e

        except httpx.TimeoutException as e:
            raise DataGouvAPIError(f"Request timed out: {url}") from e
        except httpx.RequestError as e:
            raise DataGouvAPIError(f"Request failed: {e}") from e

    @staticmethod
    def validate_url(url: str) -> None:
        """Validate that a URL uses an allowed scheme (HTTPS only).

        Args:
            url: URL to validate.

        Raises:
            ValueError: If the URL scheme is not allowed.
        """
        parsed = urlparse(url)
        if parsed.scheme not in ALLOWED_URL_SCHEMES:
            raise ValueError(
                f"URL scheme '{parsed.scheme}' not allowed. "
                f"Only {', '.join(ALLOWED_URL_SCHEMES)} URLs are accepted."
            )

    async def _get(
        self,
        base_url: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a GET request to an API endpoint.

        Args:
            base_url: Base URL for the API.
            endpoint: API endpoint path.
            params: Query parameters.

        Returns:
            Parsed JSON response.
        """
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        return await self._request("GET", url, params=params)
