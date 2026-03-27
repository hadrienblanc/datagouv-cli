"""JSON output formatting utilities."""

import json
from typing import Any

from rich.console import Console
from rich.syntax import Syntax


def format_json(
    data: dict[str, Any] | list[dict[str, Any]],
    console: Console | None = None,
) -> None:
    """Format and print data as JSON.

    Args:
        data: Data to format.
        console: Rich console instance.
    """
    console = console or Console()

    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
    console.print(syntax)


def format_raw_json(data: dict[str, Any] | list[dict[str, Any]]) -> str:
    """Format data as raw JSON string.

    Args:
        data: Data to format.

    Returns:
        JSON string without styling.
    """
    return json.dumps(data, indent=2, ensure_ascii=False)
