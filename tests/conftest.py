"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def mock_dataset_response() -> dict:
    """Sample dataset search response from data.gouv.fr API."""
    return {
        "data": [
            {
                "id": "test-dataset-id",
                "title": "Test Dataset",
                "description": "A test dataset for unit testing",
                "page": "https://www.data.gouv.fr/fr/datasets/test-dataset/",
                "organization": {"name": "Test Org", "id": "test-org-id"},
                "tags": ["test", "sample"],
                "resources": [{"id": "resource-1", "title": "Resource 1"}],
            }
        ],
        "next_page": None,
        "page": 1,
        "pagesize": 20,
        "total": 1,
    }


@pytest.fixture
def mock_single_dataset() -> dict:
    """Sample single dataset response."""
    return {
        "id": "test-dataset-id",
        "title": "Test Dataset",
        "description": "A detailed test dataset",
        "page": "https://www.data.gouv.fr/fr/datasets/test-dataset/",
        "organization": {
            "name": "Test Organization",
            "id": "test-org-id",
            "logo": "https://example.com/logo.png",
        },
        "tags": ["test", "sample", "data"],
        "resources": [
            {
                "id": "resource-1",
                "title": "CSV Resource",
                "format": "csv",
                "mime": "text/csv",
                "filesize": 1024,
                "url": "https://example.com/data.csv",
            }
        ],
        "created_at": "2024-01-01T00:00:00",
        "last_modified": "2024-06-01T00:00:00",
        "license": "License Ouverte",
    }
