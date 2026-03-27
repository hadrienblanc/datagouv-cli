"""Commands module."""

from typing import Any

import anyio


def run_async(coro: Any) -> Any:
    """Run async function in sync context."""
    return anyio.run(lambda: coro)
