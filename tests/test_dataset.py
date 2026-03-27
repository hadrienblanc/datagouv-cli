"""Tests for the dataset command."""

import pytest
import respx
from httpx import Response
from typer.testing import CliRunner

from cli_gouv.main import app

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
def mock_resources_list() -> list[dict]:
    """Sample resources list."""
    return [
        {
            "id": "resource-1",
            "title": "Population 2024",
            "format": "csv",
            "mime": "text/csv",
            "filesize": 1024000,
            "last_modified": "2024-05-01T00:00:00",
        },
        {
            "id": "resource-2",
            "title": "Population 2023",
            "format": "xlsx",
            "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "filesize": 2048000,
            "last_modified": "2024-01-01T00:00:00",
        },
    ]


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
        """Test dataset command help."""
        result = runner.invoke(app, ["dataset", "--help"])
        assert result.exit_code == 0
        assert "show" in result.stdout.lower()
        assert "resources" in result.stdout.lower()
        assert "metrics" in result.stdout.lower()

    def test_dataset_show_help(self) -> None:
        """Test dataset show command help."""
        result = runner.invoke(app, ["dataset", "show", "--help"])
        assert result.exit_code == 0
        assert "dataset_id" in result.stdout.lower()

    def test_dataset_resources_help(self) -> None:
        """Test dataset resources command help."""
        result = runner.invoke(app, ["dataset", "resources", "--help"])
        assert result.exit_code == 0
        assert "dataset_id" in result.stdout.lower()

    def test_dataset_metrics_help(self) -> None:
        """Test dataset metrics command help."""
        result = runner.invoke(app, ["dataset", "metrics", "--help"])
        assert result.exit_code == 0
        assert "dataset_id" in result.stdout.lower()
