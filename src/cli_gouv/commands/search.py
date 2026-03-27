"""Search command for datasets and dataservices."""

from typing import Any, Optional

import anyio
import typer
from rich.console import Console

from cli_gouv.api.datasets import DatasetsClient
from cli_gouv.api.dataservices import DataservicesClient
from cli_gouv.output.json import format_json
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


def _run_async(coro: Any) -> Any:
    """Run async function in sync context."""
    return anyio.from_thread.run(coro)


@app.command("datasets")
def search_datasets(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Search query"),
    page: int = typer.Option(1, "--page", "-p", min=1, help="Page number"),
    page_size: int = typer.Option(20, "--size", "-s", min=1, max=100, help="Results per page"),
    organization: Optional[str] = typer.Option(None, "--org", "-o", help="Filter by organization"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    sort: Optional[str] = typer.Option(None, "--sort", help="Sort by field (e.g., '-created', 'title')"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Search for datasets on data.gouv.fr.

    Examples:
        cli-gouv search datasets "population"
        cli-gouv search datasets "immobilier" --org INSEE --tag logement
        cli-gouv search datasets "énergie" --sort -created --size 50
    """

    async def _search() -> None:
        async with DatasetsClient() as client:
            result = await client.search(
                query=query,
                page=page,
                page_size=page_size,
                organization=organization,
                tag=tag,
                sort=sort,
            )

            if json_output:
                format_json(result, console)
            else:
                format_datasets_table(result.get("data", []), console)
                format_pagination_info(
                    result.get("page", page),
                    result.get("pagesize", page_size),
                    result.get("total", 0),
                    console,
                )

    try:
        _run_async(_search())
    except ValueError as e:
        format_error(str(e), console)
        raise typer.Exit(1)
    except Exception as e:
        format_error(f"Search failed: {e}", console)
        raise typer.Exit(1)


@app.command("dataservices")
def search_dataservices(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Search query"),
    page: int = typer.Option(1, "--page", "-p", min=1, help="Page number"),
    page_size: int = typer.Option(20, "--size", "-s", min=1, max=100, help="Results per page"),
    organization: Optional[str] = typer.Option(None, "--org", "-o", help="Filter by organization"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Search for dataservices (external APIs) on data.gouv.fr.

    Examples:
        cli-gouv search dataservices "adresse"
        cli-gouv search dataservices "géocodage" --org ban
    """

    async def _search() -> None:
        async with DataservicesClient() as client:
            result = await client.search(
                query=query,
                page=page,
                page_size=page_size,
                organization=organization,
                tag=tag,
            )

            if json_output:
                format_json(result, console)
            else:
                format_dataservices_table(result.get("data", []), console)
                format_pagination_info(
                    result.get("page", page),
                    result.get("pagesize", page_size),
                    result.get("total", 0),
                    console,
                )

    try:
        _run_async(_search())
    except ValueError as e:
        format_error(str(e), console)
        raise typer.Exit(1)
    except Exception as e:
        format_error(f"Search failed: {e}", console)
        raise typer.Exit(1)
