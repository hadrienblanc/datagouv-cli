"""Tests for the dataservice command."""

import pytest
import respx
from httpx import Response
from typer.testing import CliRunner

from datagouv_cli.main import app

runner = CliRunner()


@pytest.fixture
def mock_dataservice_detail() -> dict:
    """Sample dataservice detail response."""
    return {
        "id": "dataservice-1",
        "title": "API Géo",
        "description": "API de géocodage et recherche d'adresses",
        "page": "https://www.data.gouv.fr/fr/dataservices/api-geo/",
        "organization": {
            "name": "IGN",
            "id": "ign",
            "logo": "https://example.com/logo.png",
        },
        "base_api_url": "https://api.geo.gouv.fr",
        "openapi_url": "https://api.geo.gouv.fr/openapi.json",
        "tags": ["geocodage", "adresse"],
        "license": "Open License",
        "created_at": "2024-01-01T00:00:00",
        "last_modified": "2024-06-01T00:00:00",
    }


@pytest.fixture
def mock_openapi_spec() -> dict:
    """Sample OpenAPI specification."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "API Géo",
            "version": "1.0.0",
            "description": "API de géocodage et recherche d'adresses",
        },
        "paths": {
            "/search": {
                "get": {
                    "summary": "Recherche d'adresses",
                    "parameters": [],
                },
            },
            "/reverse": {
                "get": {
                    "summary": "Géocodage inverse",
                    "parameters": [],
                },
            },
            "/autocomplete": {
                "get": {
                    "summary": "Autocomplétion d'adresses",
                    "parameters": [],
                },
            },
        },
    }


class TestDataserviceCommand:
    """Tests for dataservice command group."""

    def test_dataservice_help(self) -> None:
        """Test dataservice command help."""
        result = runner.invoke(app, ["dataservice", "--help"])
        assert result.exit_code == 0
        assert "show" in result.stdout.lower()
        assert "openapi" in result.stdout.lower()

    def test_dataservice_show_help(self) -> None:
        """Test dataservice show command help."""
        result = runner.invoke(app, ["dataservice", "show", "--help"])
        assert result.exit_code == 0
        assert "dataservice_id" in result.stdout.lower()

    def test_dataservice_openapi_help(self) -> None:
        """Test dataservice openapi command help."""
        result = runner.invoke(app, ["dataservice", "openapi", "--help"])
        assert result.exit_code == 0
        assert "dataservice_id" in result.stdout.lower()

    @respx.mock
    def test_dataservice_show_success(self, mock_dataservice_detail: dict) -> None:
        """Test successful dataservice show."""
        respx.get("https://www.data.gouv.fr/api/1/dataservices/dataservice-1/").mock(
            return_value=Response(200, json=mock_dataservice_detail)
        )

        result = runner.invoke(app, ["dataservice", "show", "dataservice-1"])
        assert result.exit_code == 0
        assert "API Géo" in result.stdout

    @respx.mock
    def test_dataservice_show_json_output(self, mock_dataservice_detail: dict) -> None:
        """Test dataservice show with JSON output."""
        respx.get("https://www.data.gouv.fr/api/1/dataservices/dataservice-1/").mock(
            return_value=Response(200, json=mock_dataservice_detail)
        )

        result = runner.invoke(app, ["dataservice", "show", "dataservice-1", "--json"])
        assert result.exit_code == 0
        assert '"id": "dataservice-1"' in result.stdout

    @respx.mock
    def test_dataservice_show_not_found(self) -> None:
        """Test dataservice show with non-existent ID."""
        respx.get("https://www.data.gouv.fr/api/1/dataservices/nonexistent/").mock(
            return_value=Response(404, json={"message": "Not found"})
        )

        result = runner.invoke(app, ["dataservice", "show", "nonexistent"])
        assert result.exit_code == 1
        assert "error" in result.stdout.lower()

    @respx.mock
    def test_dataservice_openapi_success(
        self,
        mock_dataservice_detail: dict,
        mock_openapi_spec: dict,
    ) -> None:
        """Test successful openapi spec retrieval."""
        respx.get("https://www.data.gouv.fr/api/1/dataservices/dataservice-1/").mock(
            return_value=Response(200, json=mock_dataservice_detail)
        )
        respx.get("https://api.geo.gouv.fr/openapi.json").mock(
            return_value=Response(200, json=mock_openapi_spec)
        )

        result = runner.invoke(app, ["dataservice", "openapi", "dataservice-1"])
        assert result.exit_code == 0
        assert "API Géo" in result.stdout
        assert "/search" in result.stdout

    @respx.mock
    def test_dataservice_openapi_json_output(
        self,
        mock_dataservice_detail: dict,
        mock_openapi_spec: dict,
    ) -> None:
        """Test openapi with JSON output."""
        respx.get("https://www.data.gouv.fr/api/1/dataservices/dataservice-1/").mock(
            return_value=Response(200, json=mock_dataservice_detail)
        )
        respx.get("https://api.geo.gouv.fr/openapi.json").mock(
            return_value=Response(200, json=mock_openapi_spec)
        )

        result = runner.invoke(app, ["dataservice", "openapi", "dataservice-1", "--json"])
        assert result.exit_code == 0
        assert '"openapi"' in result.stdout

    @respx.mock
    def test_dataservice_openapi_no_url(self, mock_dataservice_detail: dict) -> None:
        """Test openapi when dataservice has no OpenAPI URL."""
        # Remove openapi_url from fixture
        mock_dataservice_detail["openapi_url"] = None
        respx.get("https://www.data.gouv.fr/api/1/dataservices/dataservice-1/").mock(
            return_value=Response(200, json=mock_dataservice_detail)
        )

        result = runner.invoke(app, ["dataservice", "openapi", "dataservice-1"])
        assert result.exit_code == 1
        assert "error" in result.stdout.lower()
