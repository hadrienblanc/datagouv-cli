"""Tests for main CLI entry point."""

from typer.testing import CliRunner

from datagouv_cli.main import app

runner = CliRunner()


def test_version() -> None:
    """Test --version flag."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "datagouv-cli version" in result.stdout


def test_help() -> None:
    """Test --help flag."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "data.gouv.fr" in result.stdout
    assert "Open Data" in result.stdout


def test_no_args_shows_help() -> None:
    """Test that no args shows help content."""
    result = runner.invoke(app, [])
    # Typer shows help when no_args_is_help=True, but may exit with code 2
    # The important thing is that help content is shown, not the error message
    assert "data.gouv.fr" in result.stdout
    assert "Commands" in result.stdout  # Shows available commands


def test_search_help() -> None:
    """Test search command help."""
    result = runner.invoke(app, ["search", "--help"])
    assert result.exit_code == 0
    assert "datasets" in result.stdout.lower()
    assert "dataservices" in result.stdout.lower()
