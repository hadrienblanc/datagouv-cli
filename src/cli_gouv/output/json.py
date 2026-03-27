"""JSON output formatting utilities."""

import json
from typing import Any


def format_raw_json(data: dict[str, Any] | list[dict[str, Any]]) -> str:
    """Format data as raw JSON string without styling.

    Use for piping to other tools.

    Args:
        data: Data to format.

    Returns:
        JSON string without ANSI styling.
    """
    return json.dumps(data, indent=2, ensure_ascii=False)
