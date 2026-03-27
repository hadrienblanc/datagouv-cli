"""Main entry point for CLI-Gouv."""

import typer
from rich.console import Console

from cli_gouv import __version__

app = typer.Typer(
    name="cli-gouv",
    help="CLI to interact with data.gouv.fr - French Open Data platform",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"cli-gouv version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """CLI to interact with data.gouv.fr - French Open Data platform.

    Search datasets, explore resources, query data, and more.
    """
    pass


@app.command()
def hello(
    name: str = typer.Argument("World", help="Name to greet"),
) -> None:
    """Simple greeting command for testing."""
    console.print(f"[green]Hello {name}![/green] from CLI-Gouv")


if __name__ == "__main__":
    app()
