"""Tests for the dataset command."""

import json

import pytest
import respx
from httpx import Response
from typer.testing import CliRunner

from datagouv_cli.api.client import BaseClient
from datagouv_cli.main import app

runner = CliRunner()


@pytest.fixture
def mock_dataset_detail() -> dict:
    """Sample dataset detail response."""
    return {
        "id": "dataset-1",
        "title": "Population française",
        "description": "Données de population par commune",
        "page": "https://www.data.gouv.fr/fr/datasets/dataset-1/",
        "organization": {
            "name": "INSEE",
            "id": "insee",
            "logo": "https://example.com/logo.png",
        },
        "tags": ["population", "demographie"],
        "license": "Licence Ouverte",
        "created_at": "2024-01-01T00:00:00",
        "last_modified": "2024-06-01T00:00:00",
        "resources": [
            {
                "id": "resource-1",
                "title": "Population 2024",
                "format": "csv",
                "mime": "text/csv",
                "filesize": 1024000,
                "url": "https://example.com/data.csv",
                "last_modified": "2024-05-01T00:00:00",
            }
        ],
    }


@pytest.fixture
def mock_metrics_response() -> dict:
    """Sample metrics response."""
    return {
        "dataset_id": "dataset-1",
        "metrics": [
            {"month": "2024-06", "views": 1500, "downloads": 300},
            {"month": "2024-05", "views": 1200, "downloads": 250},
            {"month": "2024-04", "views": 1100, "downloads": 200},
        ],
    }


class TestDatasetCommand:
    """Tests for dataset command group."""

    def test_dataset_help(self) -> None:
        result = runner.invoke(app, ["dataset", "--help"])
        assert result.exit_code == 0
        assert "show" in result.stdout.lower()
        assert "resources" in result.stdout.lower()
        assert "metrics" in result.stdout.lower()

    def test_dataset_show_help(self) -> None:
        result = runner.invoke(app, ["dataset", "show", "--help"])
        assert result.exit_code == 0
        assert "dataset_id" in result.stdout.lower()

    def test_dataset_resources_help(self) -> None:
        result = runner.invoke(app, ["dataset", "resources", "--help"])
        assert result.exit_code == 0
        assert "dataset_id" in result.stdout.lower()

    def test_dataset_metrics_help(self) -> None:
        result = runner.invoke(app, ["dataset", "metrics", "--help"])
        assert result.exit_code == 0
        assert "dataset_id" in result.stdout.lower()

    @respx.mock
    def test_dataset_show_success(self, mock_dataset_detail: dict) -> None:
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/dataset-1/").mock(
            return_value=Response(200, json=mock_dataset_detail)
        )
        result = runner.invoke(app, ["dataset", "show", "dataset-1"])
        assert result.exit_code == 0
        assert "Population française" in result.stdout
        assert "INSEE" in result.stdout

    @respx.mock
    def test_dataset_show_json(self, mock_dataset_detail: dict) -> None:
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/dataset-1/").mock(
            return_value=Response(200, json=mock_dataset_detail)
        )
        result = runner.invoke(app, ["dataset", "show", "dataset-1", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.stdout)
        assert parsed["title"] == "Population française"

    @respx.mock
    def test_dataset_show_not_found(self) -> None:
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/unknown/").mock(
            return_value=Response(404, text="Not found")
        )
        result = runner.invoke(app, ["dataset", "show", "unknown"])
        assert result.exit_code == 1
        assert "error" in result.stdout.lower()

    @respx.mock
    def test_dataset_resources_success(self, mock_dataset_detail: dict) -> None:
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/dataset-1/").mock(
            return_value=Response(200, json=mock_dataset_detail)
        )
        result = runner.invoke(app, ["dataset", "resources", "dataset-1"])
        assert result.exit_code == 0
        assert "Population 2024" in result.stdout
        assert "csv" in result.stdout.lower()

    @respx.mock
    def test_dataset_resources_json(self, mock_dataset_detail: dict) -> None:
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/dataset-1/").mock(
            return_value=Response(200, json=mock_dataset_detail)
        )
        result = runner.invoke(app, ["dataset", "resources", "dataset-1", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.stdout)
        assert isinstance(parsed, list)
        assert parsed[0]["id"] == "resource-1"

    @respx.mock
    def test_dataset_metrics_success(self, mock_metrics_response: dict) -> None:
        respx.get(f"{BaseClient.METRICS_API_URL}/datasets/dataset-1/").mock(
            return_value=Response(200, json=mock_metrics_response)
        )
        result = runner.invoke(app, ["dataset", "metrics", "dataset-1"])
        assert result.exit_code == 0
        assert "2024-06" in result.stdout
        assert "1500" in result.stdout

    @respx.mock
    def test_dataset_metrics_json(self, mock_metrics_response: dict) -> None:
        respx.get(f"{BaseClient.METRICS_API_URL}/datasets/dataset-1/").mock(
            return_value=Response(200, json=mock_metrics_response)
        )
        result = runner.invoke(app, ["dataset", "metrics", "dataset-1", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.stdout)
        assert "metrics" in parsed
