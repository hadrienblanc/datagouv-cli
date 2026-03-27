"""Output formatting utilities using Rich."""

from typing import Any

from rich.console import Console
from rich.table import Table


def format_datasets_table(
    datasets: list[dict[str, Any]],
    console: Console | None = None,
) -> None:
    """Format and print datasets as a table.

    Args:
        datasets: List of dataset objects from API.
        console: Rich console instance (creates new one if None).
    """
    console = console or Console()

    if not datasets:
        console.print("[yellow]No datasets found.[/yellow]")
        return

    table = Table(title="Datasets")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="green")
    table.add_column("Organization", style="blue")
    table.add_column("Resources", justify="right")
    table.add_column("Last Modified", style="dim")

    for ds in datasets:
        org = ds.get("organization", {})
        org_name = org.get("name", org.get("acronym", "N/A")) if org else "N/A"

        table.add_row(
            ds.get("id", "N/A")[:20],
            ds.get("title", "N/A")[:50],
            org_name[:30],
            str(len(ds.get("resources", []))),
            ds.get("last_modified", "N/A")[:10] if ds.get("last_modified") else "N/A",
        )

    console.print(table)


def format_dataservices_table(
    dataservices: list[dict[str, Any]],
    console: Console | None = None,
) -> None:
    """Format and print dataservices as a table.

    Args:
        dataservices: List of dataservice objects from API.
        console: Rich console instance (creates new one if None).
    """
    console = console or Console()

    if not dataservices:
        console.print("[yellow]No dataservices found.[/yellow]")
        return

    table = Table(title="Dataservices (External APIs)")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="green")
    table.add_column("Organization", style="blue")
    table.add_column("Base URL", style="dim")

    for ds in dataservices:
        org = ds.get("organization", {})
        org_name = org.get("name", "N/A") if org else "N/A"
        base_url = ds.get("base_api_url", "N/A")

        table.add_row(
            ds.get("id", "N/A")[:20],
            ds.get("title", "N/A")[:40],
            org_name[:25],
            base_url[:35] if base_url else "N/A",
        )

    console.print(table)


def format_pagination_info(
    page: int,
    page_size: int,
    total: int,
    console: Console | None = None,
) -> None:
    """Format and print pagination information.

    Args:
        page: Current page number.
        page_size: Number of items per page.
        total: Total number of items.
        console: Rich console instance.
    """
    console = console or Console()

    start = (page - 1) * page_size + 1
    end = min(page * page_size, total)

    console.print(
        f"\n[dim]Showing {start}-{end} of {total} results (page {page})[/dim]"
    )


def format_error(message: str, console: Console | None = None) -> None:
    """Format and print an error message.

    Args:
        message: Error message.
        console: Rich console instance.
    """
    console = console or Console()
    console.print(f"[red]Error:[/red] {message}")
