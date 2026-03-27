"""Tests for main CLI entry point."""

from typer.testing import CliRunner

from cli_gouv.main import app

runner = CliRunner()


def test_version() -> None:
    """Test --version flag."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "cli-gouv version" in result.stdout


def test_help() -> None:
    """Test --help flag."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "data.gouv.fr" in result.stdout
    assert "Open Data" in result.stdout


def test_hello_command() -> None:
    """Test hello command."""
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello World!" in result.stdout


def test_hello_with_name() -> None:
    """Test hello command with custom name."""
    result = runner.invoke(app, ["hello", "data.gouv"])
    assert result.exit_code == 0
    assert "Hello data.gouv!" in result.stdout
