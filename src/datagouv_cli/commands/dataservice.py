"""Dataservice command for viewing external API details."""

from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from datagouv_cli.api.client import DataGouvAPIError
from datagouv_cli.api.dataservices import DataservicesClient, OpenAPIFetchError
from datagouv_cli.commands import run_async
from datagouv_cli.output.json import format_raw_json
from datagouv_cli.output.table import safe_str, format_error

app = typer.Typer(
    name="dataservice",
    help="View dataservice (external API) details and OpenAPI specs",
)
console = Console()




@app.command("show")
def show_dataservice(
    dataservice_id: str = typer.Argument(..., help="Dataservice ID or slug"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Show detailed information about a dataservice (external API).

    Dataservices are external APIs registered on data.gouv.fr.

    Examples:
        datagouv-cli dataservice show "api-geo"
        datagouv-cli dataservice show "5c4ae510634f413779c9a773" --json
    """

    async def _show() -> Any:
        async with DataservicesClient() as client:
            return await client.get_dataservice(dataservice_id)

    try:
        result = run_async(_show())

        if json_output:
            print(format_raw_json(result))
        else:
            _format_dataservice_detail(result, console)

    except ValueError as e:
        format_error(str(e), console)
        raise typer.Exit(1)
    except DataGouvAPIError as e:
        format_error(f"API error: {e.message}", console)
        raise typer.Exit(1)
    except (OSError, RuntimeError) as e:
        format_error(f"Failed to get dataservice: {e}", console)
        raise typer.Exit(1)


@app.command("openapi")
def show_openapi(
    dataservice_id: str = typer.Argument(..., help="Dataservice ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Show OpenAPI specification for a dataservice.

    Displays available endpoints, methods, and parameters.

    Examples:
        datagouv-cli dataservice openapi "api-geo"
        datagouv-cli dataservice openapi "5c4ae510634f413779c9a773" --json
    """

    async def _openapi() -> Any:
        async with DataservicesClient() as client:
            return await client.get_openapi_spec(dataservice_id)

    try:
        result = run_async(_openapi())

        if json_output:
            print(format_raw_json(result))
        else:
            _format_openapi_spec(result, console)

    except ValueError as e:
        format_error(str(e), console)
        raise typer.Exit(1)
    except OpenAPIFetchError as e:
        format_error(f"OpenAPI error: {e.message}", console)
        raise typer.Exit(1)
    except DataGouvAPIError as e:
        format_error(f"API error: {e.message}", console)
        raise typer.Exit(1)
    except (OSError, RuntimeError) as e:
        format_error(f"Failed to get OpenAPI spec: {e}", console)
        raise typer.Exit(1)


def _format_dataservice_detail(dataservice: dict[str, Any], console: Console) -> None:
    """Format and print detailed dataservice information."""
    # Title panel
    title = dataservice.get("title", "Untitled")
    console.print(Panel(title, style="bold green", title="Dataservice"))

    # Basic info table
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Key", style="cyan")
    info_table.add_column("Value")

    org = dataservice.get("organization") or {}
    org_name = org.get("name") or org.get("acronym") or "N/A"

    info_table.add_row("ID", safe_str(dataservice.get("id"), 50))
    info_table.add_row("Organization", org_name)
    info_table.add_row("Base URL", safe_str(dataservice.get("base_api_url"), 80))
    info_table.add_row("OpenAPI URL", safe_str(dataservice.get("openapi_url"), 80))
    info_table.add_row("License", safe_str(dataservice.get("license"), 30))
    info_table.add_row("Created", safe_str(dataservice.get("created_at") or "N/A", 20))
    info_table.add_row("Last Modified", safe_str(dataservice.get("last_modified") or "N/A", 20))
    info_table.add_row("Page", safe_str(dataservice.get("page"), 80))

    console.print(info_table)

    # Description
    description = dataservice.get("description")
    if description:
        console.print(f"\n[bold]Description:[/bold]")
        # Truncate long descriptions
        if len(description) > 500:
            description = description[:500] + "..."
        console.print(description)

    # Tags
    tags = dataservice.get("tags") or []
    if tags:
        console.print(f"\n[bold]Tags:[/bold] {', '.join(tags)}")


def _format_openapi_spec(spec: dict[str, Any], console: Console) -> None:
    """Format and print OpenAPI specification."""
    # Title and version
    info = spec.get("info", {})
    title = info.get("title", "Untitled API")
    version = info.get("version", "N/A")
    description = info.get("description", "")

    console.print(Panel(f"{title} (v{version})", style="bold green", title="OpenAPI Spec"))

    if description:
        # Truncate long descriptions
        if len(description) > 300:
            description = description[:300] + "..."
        console.print(f"\n[dim]{description}[/dim]")

    # Endpoints table
    paths = spec.get("paths", {})
    if not paths:
        console.print("[yellow]No endpoints defined in this spec.[/yellow]")
        return

    table = Table(title="Endpoints")
    table.add_column("Method", style="cyan", max_width=8)
    table.add_column("Path", style="green", max_width=50)
    table.add_column("Summary", style="dim", max_width=50)

    # Collect all endpoints
    endpoints = []
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ["get", "post", "put", "patch", "delete"]:
                summary = details.get("summary", "") or details.get("description", "")
                endpoints.append((method.upper(), path, summary))

    # Sort by path and display (limit to 50)
    endpoints.sort(key=lambda x: x[1])
    for method, path, summary in endpoints[:50]:
        table.add_row(
            method,
            safe_str(path, 50),
            safe_str(summary, 50),
        )

    console.print(table)

    if len(endpoints) > 50:
        console.print(f"\n[dim]Showing 50 of {len(endpoints)} endpoints[/dim]")
