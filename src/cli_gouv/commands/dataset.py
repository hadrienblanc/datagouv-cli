"""Dataset command for viewing dataset details."""

from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli_gouv.api.client import DataGouvAPIError
from cli_gouv.api.datasets import DatasetsClient
from cli_gouv.api.metrics import MetricsClient
from cli_gouv.commands import run_async
from cli_gouv.output.json import format_raw_json
from cli_gouv.output.table import safe_str, format_error

app = typer.Typer(
    name="dataset",
    help="View dataset details, resources, and metrics",
)
console = Console()




@app.command("show")
def show_dataset(
    dataset_id: str = typer.Argument(..., help="Dataset ID or slug"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Show detailed information about a dataset.

    Examples:
        cli-gouv dataset show "population-francaise"
        cli-gouv dataset show "5c4ae510634f413779c9a773" --json
    """

    async def _show() -> Any:
        async with DatasetsClient() as client:
            return await client.get_dataset(dataset_id)

    try:
        result = run_async(_show())

        if json_output:
            print(format_raw_json(result))
        else:
            _format_dataset_detail(result, console)

    except ValueError as e:
        format_error(str(e), console)
        raise typer.Exit(1)
    except DataGouvAPIError as e:
        format_error(f"API error: {e.message}", console)
        raise typer.Exit(1)
    except (OSError, RuntimeError) as e:
        format_error(f"Failed to get dataset: {e}", console)
        raise typer.Exit(1)


@app.command("resources")
def list_resources(
    dataset_id: str = typer.Argument(..., help="Dataset ID or slug"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List all resources (files) in a dataset.

    Examples:
        cli-gouv dataset resources "population-francaise"
        cli-gouv dataset resources "5c4ae510634f413779c9a773" --json
    """

    async def _list() -> Any:
        async with DatasetsClient() as client:
            return await client.list_resources(dataset_id)

    try:
        resources = run_async(_list())

        if json_output:
            print(format_raw_json(resources))
        else:
            _format_resources_table(resources, console)

    except ValueError as e:
        format_error(str(e), console)
        raise typer.Exit(1)
    except DataGouvAPIError as e:
        format_error(f"API error: {e.message}", console)
        raise typer.Exit(1)
    except (OSError, RuntimeError) as e:
        format_error(f"Failed to list resources: {e}", console)
        raise typer.Exit(1)


@app.command("metrics")
def show_metrics(
    dataset_id: str = typer.Argument(..., help="Dataset ID"),
    limit: int = typer.Option(12, "--limit", "-l", min=1, max=100, help="Months to show"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Show metrics (views, downloads) for a dataset.

    Examples:
        cli-gouv dataset metrics "5c4ae510634f413779c9a773"
        cli-gouv dataset metrics "5c4ae510634f413779c9a773" --limit 24 --json
    """

    async def _metrics() -> Any:
        async with MetricsClient() as client:
            return await client.get_dataset_metrics(dataset_id, limit)

    try:
        result = run_async(_metrics())

        if json_output:
            print(format_raw_json(result))
        else:
            _format_metrics_table(result, console)

    except ValueError as e:
        format_error(str(e), console)
        raise typer.Exit(1)
    except DataGouvAPIError as e:
        format_error(f"API error: {e.message}", console)
        raise typer.Exit(1)
    except (OSError, RuntimeError) as e:
        format_error(f"Failed to get metrics: {e}", console)
        raise typer.Exit(1)


def _format_dataset_detail(dataset: dict[str, Any], console: Console) -> None:
    """Format and print detailed dataset information."""
    # Title panel
    title = dataset.get("title", "Untitled")
    console.print(Panel(title, style="bold green", title="Dataset"))

    # Basic info table
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Key", style="cyan")
    info_table.add_column("Value")

    org = dataset.get("organization") or {}
    org_name = org.get("name") or org.get("acronym") or "N/A"

    info_table.add_row("ID", safe_str(dataset.get("id"), 50))
    info_table.add_row("Organization", org_name)
    info_table.add_row("License", safe_str(dataset.get("license"), 30))
    info_table.add_row("Created", safe_str(dataset.get("created_at") or "N/A", 20))
    info_table.add_row("Last Modified", safe_str(dataset.get("last_modified") or "N/A", 20))
    info_table.add_row("Page", safe_str(dataset.get("page"), 80))

    console.print(info_table)

    # Description
    description = dataset.get("description")
    if description:
        console.print(f"\n[bold]Description:[/bold]")
        # Truncate long descriptions
        if len(description) > 500:
            description = description[:500] + "..."
        console.print(description)

    # Tags
    tags = dataset.get("tags") or []
    if tags:
        console.print(f"\n[bold]Tags:[/bold] {', '.join(tags)}")

    # Resources summary
    resources = dataset.get("resources") or []
    console.print(f"\n[bold]Resources:[/bold] {len(resources)} file(s)")

    if resources:
        _format_resources_table(resources, console, show_title=False)


def _format_resources_table(
    resources: list[dict[str, Any]],
    console: Console,
    show_title: bool = True,
) -> None:
    """Format and print resources as a table."""
    if not resources:
        console.print("[yellow]No resources found.[/yellow]")
        return

    table = Table(title="Resources" if show_title else None)
    table.add_column("ID", style="cyan", max_width=20)
    table.add_column("Title", style="green", max_width=40)
    table.add_column("Format", style="blue", max_width=8)
    table.add_column("Size", justify="right", max_width=10)
    table.add_column("Last Modified", style="dim", max_width=12)

    for res in resources:
        filesize = res.get("filesize")
        if filesize:
            # Convert to human readable
            if filesize >= 1024 * 1024:
                size_str = f"{filesize / (1024 * 1024):.1f} MB"
            elif filesize >= 1024:
                size_str = f"{filesize / 1024:.1f} KB"
            else:
                size_str = f"{filesize} B"
        else:
            size_str = "N/A"

        last_mod = res.get("last_modified")
        if last_mod:
            last_mod = last_mod[:10]
        else:
            last_mod = "N/A"

        table.add_row(
            safe_str(res.get("id"), 20),
            safe_str(res.get("title"), 40),
            safe_str(res.get("format"), 8).upper(),
            size_str,
            safe_str(last_mod, 12),
        )

    console.print(table)


def _format_metrics_table(metrics: dict[str, Any], console: Console) -> None:
    """Format and print metrics as a table."""
    data = metrics.get("metrics") or []

    if not data:
        console.print("[yellow]No metrics available.[/yellow]")
        return

    table = Table(title="Dataset Metrics (Monthly)")
    table.add_column("Month", style="cyan")
    table.add_column("Views", justify="right", style="green")
    table.add_column("Downloads", justify="right", style="blue")

    for item in data:
        table.add_row(
            safe_str(item.get("month"), 10),
            str(item.get("views", 0)),
            str(item.get("downloads", 0)),
        )

    console.print(table)

    # Summary
    total_views = sum(item.get("views", 0) for item in data)
    total_downloads = sum(item.get("downloads", 0) for item in data)
    console.print(
        f"\n[dim]Total: {total_views:,} views, {total_downloads:,} downloads[/dim]"
    )
