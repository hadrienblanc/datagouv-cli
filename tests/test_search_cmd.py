"""Tests for the search command."""

import json

import respx
from httpx import Response
from typer.testing import CliRunner

from datagouv_cli.api.client import BaseClient
from datagouv_cli.main import app

runner = CliRunner()


MOCK_DATASET_SEARCH = {
    "data": [
        {
            "id": "ds-1",
            "title": "Population INSEE",
            "organization": {"name": "INSEE"},
            "resources": [{"id": "r1"}],
            "last_modified": "2024-06-01T00:00:00",
        }
    ],
    "page": 1,
    "pagesize": 20,
    "total": 1,
}

MOCK_DATASERVICE_SEARCH = {
    "data": [
        {
            "id": "api-1",
            "title": "API Adresse",
            "organization": {"name": "BAN"},
            "base_api_url": "https://api-adresse.data.gouv.fr",
        }
    ],
    "page": 1,
    "pagesize": 20,
    "total": 1,
}


class TestSearchDatasetsCommand:

    @respx.mock
    def test_search_datasets_success(self) -> None:
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/").mock(
            return_value=Response(200, json=MOCK_DATASET_SEARCH)
        )
        result = runner.invoke(app, ["search", "datasets", "population"])
        assert result.exit_code == 0
        assert "Population INSEE" in result.stdout

    @respx.mock
    def test_search_datasets_json(self) -> None:
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/").mock(
            return_value=Response(200, json=MOCK_DATASET_SEARCH)
        )
        result = runner.invoke(app, ["search", "datasets", "population", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.stdout)
        assert parsed["total"] == 1

    @respx.mock
    def test_search_datasets_api_error(self) -> None:
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/").mock(
            return_value=Response(500, text="Server error")
        )
        result = runner.invoke(app, ["search", "datasets", "test"])
        assert result.exit_code == 1
        assert "error" in result.stdout.lower()

    @respx.mock
    def test_search_datasets_empty(self) -> None:
        empty = {"data": [], "page": 1, "pagesize": 20, "total": 0}
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/").mock(
            return_value=Response(200, json=empty)
        )
        result = runner.invoke(app, ["search", "datasets", "zzzzzzz"])
        assert result.exit_code == 0
        assert "no" in result.stdout.lower()


class TestSearchDataservicesCommand:

    @respx.mock
    def test_search_dataservices_success(self) -> None:
        respx.get(f"{BaseClient.MAIN_API_URL}/dataservices/").mock(
            return_value=Response(200, json=MOCK_DATASERVICE_SEARCH)
        )
        result = runner.invoke(app, ["search", "dataservices", "adresse"])
        assert result.exit_code == 0
        assert "API Adresse" in result.stdout

    @respx.mock
    def test_search_dataservices_json(self) -> None:
        respx.get(f"{BaseClient.MAIN_API_URL}/dataservices/").mock(
            return_value=Response(200, json=MOCK_DATASERVICE_SEARCH)
        )
        result = runner.invoke(app, ["search", "dataservices", "adresse", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.stdout)
        assert parsed["data"][0]["title"] == "API Adresse"
