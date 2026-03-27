"""Resource command for querying and downloading resources."""

from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from cli_gouv.api.client import DataGouvAPIError
from cli_gouv.api.resources import ResourceDownloadError, ResourcesClient
from cli_gouv.commands import run_async
from cli_gouv.output.json import format_raw_json
from cli_gouv.output.table import safe_str, format_error

app = typer.Typer(
    name="resource",
    help="Query and download resources (data files)",
)
console = Console()




@app.command("query")
def query_resource(
    resource_id: str = typer.Argument(..., help="Resource ID"),
    where: str | None = typer.Option(None, "--where", "-w", help="SQL-like WHERE clause"),
    page: int = typer.Option(1, "--page", "-p", min=1, help="Page number"),
    page_size: int = typer.Option(20, "--size", "-s", min=1, max=200, help="Rows per page"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Query tabular data from a resource (CSV/XLS).

    The resource must be tabular (CSV or Excel) and indexed by the Tabular API.

    Examples:
        cli-gouv resource query "abc123" --where "code_postal = '75001'"
        cli-gouv resource query "abc123" --page 2 --size 50
        cli-gouv resource query "abc123" --json
    """

    async def _query() -> Any:
        async with ResourcesClient() as client:
            return await client.query_tabular(
                resource_id=resource_id,
                query=where,
                page=page,
                page_size=page_size,
            )

    try:
        result = run_async(_query())

        if json_output:
            print(format_raw_json(result))
        else:
            _format_query_results(result, console)

    except ValueError as e:
        format_error(str(e), console)
        raise typer.Exit(1)
    except DataGouvAPIError as e:
        format_error(f"API error: {e.message}", console)
        raise typer.Exit(1)
    except (OSError, RuntimeError) as e:
        format_error(f"Query failed: {e}", console)
        raise typer.Exit(1)


@app.command("schema")
def show_schema(
    resource_id: str = typer.Argument(..., help="Resource ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Show schema (columns) for a tabular resource.

    Examples:
        cli-gouv resource schema "abc123"
        cli-gouv resource schema "abc123" --json
    """

    async def _schema() -> Any:
        async with ResourcesClient() as client:
            return await client.get_schema(resource_id)

    try:
        result = run_async(_schema())

        if json_output:
            print(format_raw_json(result))
        else:
            _format_schema(result, console)

    except ValueError as e:
        format_error(str(e), console)
        raise typer.Exit(1)
    except DataGouvAPIError as e:
        format_error(f"API error: {e.message}", console)
        raise typer.Exit(1)
    except (OSError, RuntimeError) as e:
        format_error(f"Failed to get schema: {e}", console)
        raise typer.Exit(1)


@app.command("download")
def download_resource(
    url: str = typer.Argument(..., help="Resource download URL"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Download a resource file.

    Note: Use 'dataset resources' to find the download URL for a resource.

    Examples:
        cli-gouv resource download "https://example.com/data.csv"
        cli-gouv resource download "https://example.com/data.csv" -o ./data.csv
    """

    async def _download() -> bytes:
        async with ResourcesClient() as client:
            return await client.download(url)

    try:
        content = run_async(_download())

        if output:
            # Write to file
            with open(output, "wb") as f:
                f.write(content)
            console.print(f"[green]Downloaded {len(content):,} bytes to {output}[/green]")
        else:
            # Write to stdout
            console.print(f"[dim]Downloaded {len(content):,} bytes[/dim]")
            console.print("[dim]Use --output to save to a file[/dim]")

    except ValueError as e:
        format_error(str(e), console)
        raise typer.Exit(1)
    except ResourceDownloadError as e:
        format_error(f"Download error: {e.message}", console)
        raise typer.Exit(1)
    except (OSError, RuntimeError) as e:
        format_error(f"Download failed: {e}", console)
        raise typer.Exit(1)


def _format_query_results(result: dict[str, Any], console: Console) -> None:
    """Format and print query results as a table."""
    data = result.get("data", [])

    if not data:
        console.print("[yellow]No data found.[/yellow]")
        return

    # Get column names from first row or schema
    columns = list(data[0].keys()) if data else []

    table = Table(title="Query Results")
    for col in columns[:10]:  # Limit to 10 columns for display
        table.add_column(col, max_width=30)

    for row in data[:50]:  # Limit to 50 rows for display
        table.add_row(*[safe_str(row.get(col), 30) for col in columns[:10]])

    console.print(table)

    # Pagination info
    meta = result.get("meta", {})
    total = meta.get("total", len(data))
    page_num = meta.get("page", 1)
    page_sz = meta.get("page_size", 20)

    console.print(
        f"\n[dim]Showing {len(data)} of {total:,} rows (page {page_num}, size {page_sz})[/dim]"
    )
    if total > page_sz:
        console.print("[dim]Use --page to see more results[/dim]")


def _format_schema(schema: dict[str, Any], console: Console) -> None:
    """Format and print schema information."""
    fields = schema.get("fields") or schema.get("columns") or []

    if not fields:
        console.print("[yellow]No schema information available.[/yellow]")
        return

    table = Table(title="Resource Schema")
    table.add_column("Column", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Description", style="dim")

    for field in fields:
        name = field.get("name") or field.get("columnName") or "N/A"
        field_type = field.get("type") or field.get("dataType") or "unknown"
        description = field.get("description") or field.get("comment") or ""

        table.add_row(
            safe_str(name, 40),
            safe_str(field_type, 15),
            safe_str(description, 50),
        )

    console.print(table)
