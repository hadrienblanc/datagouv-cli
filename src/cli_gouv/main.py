"""Main entry point for CLI-Gouv."""

import typer
from rich.console import Console

from cli_gouv import __version__
from cli_gouv.commands.dataset import app as dataset_app
from cli_gouv.commands.dataservice import app as dataservice_app
from cli_gouv.commands.resource import app as resource_app
from cli_gouv.commands.search import app as search_app

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


# Register sub-commands
app.add_typer(dataset_app, name="dataset")
app.add_typer(dataservice_app, name="dataservice")
app.add_typer(resource_app, name="resource")
app.add_typer(search_app, name="search")


@app.command("mcp")
def run_mcp(
    transport: str = typer.Option(
        "stdio",
        "--transport",
        "-t",
        help="Transport mode: stdio or sse",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Port for SSE transport",
    ),
) -> None:
    """Start the MCP server for LLM integration.

    Exposes data.gouv.fr tools via Model Context Protocol.

    Examples:
        cli-gouv mcp
        cli-gouv mcp --transport sse --port 8080
    """
    from cli_gouv.mcp_server import mcp as mcp_server

    if transport == "stdio":
        mcp_server.run(transport="stdio")
    elif transport == "sse":
        mcp_server.run(transport="sse", port=port)
    else:
        console.print(f"[red]Error:[/red] Unknown transport: {transport}")
        console.print("[dim]Supported: stdio, sse[/dim]")
        raise typer.Exit(1)


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


if __name__ == "__main__":
    app()
