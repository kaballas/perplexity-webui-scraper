"""Core type definitions for the Perplexity harness."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol


class PplxClient(Protocol):
    """Protocol describing the Perplexity client surface used by the harness."""

    def ask_stream(self, prompt: str) -> Iterable[object]:
        ...

    def ask_once(self, prompt: str) -> str:
        ...


@dataclass(slots=True)
class RunConfig:
    """Runtime configuration resolved from CLI arguments and environment."""

    input_path: Path
    output_path: Path
    max_records: int
    client: PplxClient


__all__ = ["PplxClient", "RunConfig"]
