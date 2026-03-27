"""Tests for the MCP server tools."""

import json

import httpx
import pytest
import respx

from datagouv_cli.api.client import BaseClient
import datagouv_cli.mcp_server as mcp_mod
from datagouv_cli.mcp_server import (
    get_dataservice_info,
    get_dataset_info,
    get_metrics,
    get_openapi_spec,
    get_resource_schema,
    list_resources,
    query_resource_data,
    search_dataservices,
    search_datasets,
)


@pytest.fixture(autouse=True)
async def _reset_shared_client():
    """Reset the shared HTTP client between tests."""
    mcp_mod._shared_http_client = None
    yield
    if mcp_mod._shared_http_client and not mcp_mod._shared_http_client.is_closed:
        await mcp_mod._shared_http_client.aclose()
    mcp_mod._shared_http_client = None


class TestSearchDatasets:
    @respx.mock
    async def test_search_returns_results(self, mock_dataset_response):
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/").mock(
            return_value=httpx.Response(200, json=mock_dataset_response)
        )
        result = json.loads(await search_datasets("population"))
        assert result["total"] == 1
        assert result["data"][0]["title"] == "Test Dataset"

    @respx.mock
    async def test_search_with_filters(self, mock_dataset_response):
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/").mock(
            return_value=httpx.Response(200, json=mock_dataset_response)
        )
        result = json.loads(
            await search_datasets(
                "test", organization="INSEE", tag="population", sort="-created"
            )
        )
        assert "data" in result

    async def test_search_invalid_page(self):
        result = json.loads(await search_datasets("test", page=0))
        assert "error" in result

    @respx.mock
    async def test_search_api_error(self):
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        result = json.loads(await search_datasets("test"))
        assert "error" in result


class TestGetDatasetInfo:
    @respx.mock
    async def test_get_dataset(self, mock_single_dataset):
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/test-id/").mock(
            return_value=httpx.Response(200, json=mock_single_dataset)
        )
        result = json.loads(await get_dataset_info("test-id"))
        assert result["title"] == "Test Dataset"

    @respx.mock
    async def test_get_dataset_not_found(self):
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/unknown/").mock(
            return_value=httpx.Response(404)
        )
        result = json.loads(await get_dataset_info("unknown"))
        assert "error" in result


class TestListResources:
    @respx.mock
    async def test_list_resources(self, mock_single_dataset):
        respx.get(f"{BaseClient.MAIN_API_URL}/datasets/test-id/").mock(
            return_value=httpx.Response(200, json=mock_single_dataset)
        )
        result = json.loads(await list_resources("test-id"))
        assert len(result) == 1
        assert result[0]["id"] == "resource-1"


class TestQueryResourceData:
    @respx.mock
    async def test_query_tabular(self):
        mock_response = {
            "data": [{"col1": "val1", "col2": "val2"}],
            "meta": {"total": 1, "page": 1, "page_size": 20},
        }
        respx.get(f"{BaseClient.TABULAR_API_URL}/resources/res-id/data/").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = json.loads(await query_resource_data("res-id"))
        assert len(result["data"]) == 1

    @respx.mock
    async def test_query_with_where(self):
        mock_response = {"data": [], "meta": {"total": 0}}
        respx.get(f"{BaseClient.TABULAR_API_URL}/resources/res-id/data/").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = json.loads(
            await query_resource_data("res-id", where="code = '75001'")
        )
        assert "data" in result

    async def test_query_invalid_page(self):
        result = json.loads(await query_resource_data("res-id", page=0))
        assert "error" in result


class TestGetResourceSchema:
    @respx.mock
    async def test_get_schema(self):
        mock_schema = {
            "fields": [
                {"name": "col1", "type": "string"},
                {"name": "col2", "type": "integer"},
            ]
        }
        respx.get(f"{BaseClient.TABULAR_API_URL}/resources/res-id/schema/").mock(
            return_value=httpx.Response(200, json=mock_schema)
        )
        result = json.loads(await get_resource_schema("res-id"))
        assert len(result["fields"]) == 2


class TestSearchDataservices:
    @respx.mock
    async def test_search(self):
        mock_response = {
            "data": [{"id": "ds-1", "title": "API Adresse"}],
            "total": 1,
            "page": 1,
        }
        respx.get(f"{BaseClient.MAIN_API_URL}/dataservices/").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = json.loads(await search_dataservices("adresse"))
        assert result["data"][0]["title"] == "API Adresse"

    async def test_search_invalid_page(self):
        result = json.loads(await search_dataservices("test", page=-1))
        assert "error" in result


class TestGetDataserviceInfo:
    @respx.mock
    async def test_get_dataservice(self):
        mock_ds = {"id": "ds-1", "title": "API Adresse", "base_api_url": "https://api.example.com"}
        respx.get(f"{BaseClient.MAIN_API_URL}/dataservices/ds-1/").mock(
            return_value=httpx.Response(200, json=mock_ds)
        )
        result = json.loads(await get_dataservice_info("ds-1"))
        assert result["title"] == "API Adresse"


class TestGetOpenAPISpec:
    @respx.mock
    async def test_get_spec(self):
        mock_ds = {"id": "ds-1", "openapi_url": "https://api.example.com/spec.json"}
        mock_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0"},
            "paths": {"/test": {"get": {"summary": "Test endpoint"}}},
        }
        respx.get(f"{BaseClient.MAIN_API_URL}/dataservices/ds-1/").mock(
            return_value=httpx.Response(200, json=mock_ds)
        )
        respx.get("https://api.example.com/spec.json").mock(
            return_value=httpx.Response(200, json=mock_spec)
        )
        result = json.loads(await get_openapi_spec("ds-1"))
        assert result["info"]["title"] == "Test API"

    @respx.mock
    async def test_no_openapi_url(self):
        mock_ds = {"id": "ds-1"}
        respx.get(f"{BaseClient.MAIN_API_URL}/dataservices/ds-1/").mock(
            return_value=httpx.Response(200, json=mock_ds)
        )
        result = json.loads(await get_openapi_spec("ds-1"))
        assert "error" in result


class TestGetMetrics:
    @respx.mock
    async def test_dataset_metrics(self):
        mock_metrics = {
            "metrics": [{"month": "2024-01", "views": 100, "downloads": 50}]
        }
        respx.get(f"{BaseClient.METRICS_API_URL}/datasets/ds-id/").mock(
            return_value=httpx.Response(200, json=mock_metrics)
        )
        result = json.loads(await get_metrics(dataset_id="ds-id"))
        assert "dataset" in result

    @respx.mock
    async def test_resource_metrics(self):
        mock_metrics = {
            "metrics": [{"month": "2024-01", "downloads": 30}]
        }
        respx.get(f"{BaseClient.METRICS_API_URL}/resources/res-id/").mock(
            return_value=httpx.Response(200, json=mock_metrics)
        )
        result = json.loads(await get_metrics(resource_id="res-id"))
        assert "resource" in result

    async def test_no_ids_provided(self):
        result = json.loads(await get_metrics())
        assert "error" in result

    async def test_invalid_limit(self):
        result = json.loads(await get_metrics(dataset_id="ds-id", limit=0))
        assert "error" in result
