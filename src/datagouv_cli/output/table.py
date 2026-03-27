"""Output formatting utilities using Rich."""

from typing import Any

from rich.console import Console
from rich.table import Table


def safe_str(value: Any, max_len: int = 50) -> str:
    """Safely convert value to string with max length.

    Args:
        value: Value to convert.
        max_len: Maximum string length.

    Returns:
        String representation, truncated if needed.
    """
    if value is None:
        return "N/A"
    text = str(value)
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


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
    table.add_column("ID", style="cyan", no_wrap=True, max_width=20)
    table.add_column("Title", style="green", max_width=50)
    table.add_column("Organization", style="blue", max_width=30)
    table.add_column("Resources", justify="right")
    table.add_column("Last Modified", style="dim", max_width=12)

    for ds in datasets:
        org = ds.get("organization") or {}
        org_name = org.get("name") or org.get("acronym") or "N/A"

        # Safely handle all values
        ds_id = safe_str(ds.get("id"), 20)
        title = safe_str(ds.get("title"), 50)
        last_modified = ds.get("last_modified")
        if last_modified:
            last_modified = safe_str(last_modified[:10], 12)
        else:
            last_modified = "N/A"

        table.add_row(
            ds_id,
            title,
            safe_str(org_name, 30),
            str(len(ds.get("resources") or [])),
            last_modified,
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
    table.add_column("ID", style="cyan", no_wrap=True, max_width=20)
    table.add_column("Title", style="green", max_width=40)
    table.add_column("Organization", style="blue", max_width=25)
    table.add_column("Base URL", style="dim", max_width=35)

    for ds in dataservices:
        org = ds.get("organization") or {}
        org_name = org.get("name") or "N/A"
        base_url = ds.get("base_api_url") or ds.get("base_url")

        table.add_row(
            safe_str(ds.get("id"), 20),
            safe_str(ds.get("title"), 40),
            safe_str(org_name, 25),
            safe_str(base_url, 35),
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

    if total == 0:
        console.print("\n[dim]No results found[/dim]")
        return

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
