"""Search command for datasets and dataservices."""

from typing import Any

import typer
from rich.console import Console

from cli_gouv.api.client import DataGouvAPIError
from cli_gouv.api.dataservices import DataservicesClient
from cli_gouv.api.datasets import DatasetsClient
from cli_gouv.commands import run_async
from cli_gouv.output.json import format_raw_json
from cli_gouv.output.table import (
    format_datasets_table,
    format_dataservices_table,
    format_error,
    format_pagination_info,
)

app = typer.Typer(
    name="search",
    help="Search datasets and dataservices on data.gouv.fr",
)
console = Console()




@app.command("datasets")
def search_datasets(
    query: str = typer.Argument(..., help="Search query"),
    page: int = typer.Option(1, "--page", "-p", min=1, help="Page number"),
    page_size: int = typer.Option(20, "--size", "-s", min=1, max=100, help="Results per page"),
    organization: str | None = typer.Option(None, "--org", "-o", help="Filter by organization"),
    tag: str | None = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    sort: str | None = typer.Option(None, "--sort", help="Sort by field (e.g., '-created', 'title')"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Search for datasets on data.gouv.fr.

    Examples:
        cli-gouv search datasets "population"
        cli-gouv search datasets "immobilier" --org INSEE --tag logement
        cli-gouv search datasets "énergie" --sort -created --size 50
    """

    async def _search() -> Any:
        async with DatasetsClient() as client:
            return await client.search(
                query=query,
                page=page,
                page_size=page_size,
                organization=organization,
                tag=tag,
                sort=sort,
            )

    try:
        result = run_async(_search())

        if json_output:
            # Output raw JSON for piping to other tools
            print(format_raw_json(result))
        else:
            data = result.get("data", [])
            format_datasets_table(data, console)
            format_pagination_info(
                result.get("page", page),
                result.get("pagesize", page_size),
                result.get("total", 0),
                console,
            )

    except ValueError as e:
        format_error(str(e), console)
        raise typer.Exit(1)
    except DataGouvAPIError as e:
        format_error(f"API error: {e.message}", console)
        raise typer.Exit(1)
    except (OSError, RuntimeError) as e:
        format_error(f"Search failed: {e}", console)
        raise typer.Exit(1)


@app.command("dataservices")
def search_dataservices(
    query: str = typer.Argument(..., help="Search query"),
    page: int = typer.Option(1, "--page", "-p", min=1, help="Page number"),
    page_size: int = typer.Option(20, "--size", "-s", min=1, max=100, help="Results per page"),
    organization: str | None = typer.Option(None, "--org", "-o", help="Filter by organization"),
    tag: str | None = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Search for dataservices (external APIs) on data.gouv.fr.

    Examples:
        cli-gouv search dataservices "adresse"
        cli-gouv search dataservices "géocodage" --org ban
    """

    async def _search() -> Any:
        async with DataservicesClient() as client:
            return await client.search(
                query=query,
                page=page,
                page_size=page_size,
                organization=organization,
                tag=tag,
            )

    try:
        result = run_async(_search())

        if json_output:
            print(format_raw_json(result))
        else:
            data = result.get("data", [])
            format_dataservices_table(data, console)
            format_pagination_info(
                result.get("page", page),
                result.get("pagesize", page_size),
                result.get("total", 0),
                console,
            )

    except ValueError as e:
        format_error(str(e), console)
        raise typer.Exit(1)
    except DataGouvAPIError as e:
        format_error(f"API error: {e.message}", console)
        raise typer.Exit(1)
    except (OSError, RuntimeError) as e:
        format_error(f"Search failed: {e}", console)
        raise typer.Exit(1)
