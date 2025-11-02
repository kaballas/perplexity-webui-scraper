"""Console utilities wrapping Rich for optional UI output."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel

__all__ = ["err", "info", "panel_status", "warn"]

_console: Optional[Console] = None


def _get_console() -> Console:
    global _console
    if _console is None:
        _console = Console()
    return _console


def info(message: str) -> None:
    _get_console().print(f"[blue]{message}[/blue]")


def warn(message: str) -> None:
    _get_console().print(f"[yellow]{message}[/yellow]")


def err(message: str) -> None:
    _get_console().print(f"[red]{message}[/red]")


@contextmanager
def panel_status(title: str, spinner: str = "dots") -> Iterator[Live]:
    """
    Context manager showing a Live panel for long-running tasks.
    Yields the active Live instance for updates.
    """
    panel = Panel("", title=title, border_style="white")
    with Live(panel, refresh_per_second=8, transient=True, console=_get_console(), auto_refresh=True) as live:
        yield live
