"""Tests for the resource command."""

import json
import os
import tempfile

import respx
from httpx import Response
from typer.testing import CliRunner

from datagouv_cli.api.client import BaseClient
from datagouv_cli.main import app

runner = CliRunner()


MOCK_TABULAR = {
    "data": [
        {"code_postal": "75001", "population": 1000},
        {"code_postal": "75002", "population": 2000},
    ],
    "meta": {"page": 1, "page_size": 20, "total": 2},
}

MOCK_SCHEMA = {
    "fields": [
        {"name": "code_postal", "type": "string", "description": "Code postal"},
        {"name": "population", "type": "integer", "description": "Population"},
    ]
}


class TestResourceQueryCommand:

    @respx.mock
    def test_query_success(self) -> None:
        respx.get(f"{BaseClient.TABULAR_API_URL}/resources/res-1/data/").mock(
            return_value=Response(200, json=MOCK_TABULAR)
        )
        result = runner.invoke(app, ["resource", "query", "res-1"])
        assert result.exit_code == 0
        assert "75001" in result.stdout

    @respx.mock
    def test_query_json(self) -> None:
        respx.get(f"{BaseClient.TABULAR_API_URL}/resources/res-1/data/").mock(
            return_value=Response(200, json=MOCK_TABULAR)
        )
        result = runner.invoke(app, ["resource", "query", "res-1", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.stdout)
        assert len(parsed["data"]) == 2

    @respx.mock
    def test_query_with_where(self) -> None:
        respx.get(f"{BaseClient.TABULAR_API_URL}/resources/res-1/data/").mock(
            return_value=Response(200, json=MOCK_TABULAR)
        )
        result = runner.invoke(
            app, ["resource", "query", "res-1", "--where", "code_postal = '75001'"]
        )
        assert result.exit_code == 0

    @respx.mock
    def test_query_api_error(self) -> None:
        respx.get(f"{BaseClient.TABULAR_API_URL}/resources/res-1/data/").mock(
            return_value=Response(500, text="Server error")
        )
        result = runner.invoke(app, ["resource", "query", "res-1"])
        assert result.exit_code == 1
        assert "error" in result.stdout.lower()


class TestResourceSchemaCommand:

    @respx.mock
    def test_schema_success(self) -> None:
        respx.get(f"{BaseClient.TABULAR_API_URL}/resources/res-1/schema/").mock(
            return_value=Response(200, json=MOCK_SCHEMA)
        )
        result = runner.invoke(app, ["resource", "schema", "res-1"])
        assert result.exit_code == 0
        assert "code_postal" in result.stdout

    @respx.mock
    def test_schema_json(self) -> None:
        respx.get(f"{BaseClient.TABULAR_API_URL}/resources/res-1/schema/").mock(
            return_value=Response(200, json=MOCK_SCHEMA)
        )
        result = runner.invoke(app, ["resource", "schema", "res-1", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.stdout)
        assert len(parsed["fields"]) == 2


class TestResourceDownloadCommand:

    @respx.mock
    def test_download_to_file(self) -> None:
        respx.get("https://example.com/data.csv").mock(
            return_value=Response(200, content=b"id,name\n1,test")
        )
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            tmp_path = f.name
        try:
            result = runner.invoke(
                app, ["resource", "download", "https://example.com/data.csv", "-o", tmp_path]
            )
            assert result.exit_code == 0
            assert "Downloaded" in result.stdout
            with open(tmp_path, "rb") as f:
                assert f.read() == b"id,name\n1,test"
        finally:
            os.unlink(tmp_path)

    @respx.mock
    def test_download_no_output(self) -> None:
        respx.get("https://example.com/data.csv").mock(
            return_value=Response(200, content=b"id,name\n1,test")
        )
        result = runner.invoke(app, ["resource", "download", "https://example.com/data.csv"])
        assert result.exit_code == 0
        assert "Downloaded" in result.stdout
        assert "--output" in result.stdout

    def test_download_rejects_http(self) -> None:
        result = runner.invoke(app, ["resource", "download", "http://example.com/data.csv"])
        assert result.exit_code == 1
        assert "error" in result.stdout.lower()
