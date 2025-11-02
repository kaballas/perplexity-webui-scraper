"""JSONL file helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

SAMPLE_RECORDS = [
    {
        "Title": "SAP SuccessFactors Recruitement",
        "Description": (
            "SAP SuccessFactors Recruitment: assess whether the solution provides data export "
            "capability in different formats (e.g., CSV, Excel, PDF) for hiring managers, HR "
            "business partners, and recruitment super users for all recruitment data stored and created."
        ),
        "Area": [],
        "Product": [],
    },
]

__all__ = ["ensure_sample_input", "read_jsonl", "write_jsonl"]


def ensure_sample_input(path: Path) -> None:
    """Create a sample JSONL file for test runs (overwrites existing content)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(record, ensure_ascii=False) + "\n" for record in SAMPLE_RECORDS]
    path.write_text("".join(lines), encoding="utf-8")


def read_jsonl(path: Path, limit: int | None = None) -> List[dict]:
    """Read a JSONL file into a list of dicts (capped by ``limit`` when provided)."""
    records: List[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle, start=1):
            if limit is not None and len(records) >= limit:
                break
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {idx}: {exc}") from exc
    return records


def write_jsonl(path: Path, records: Iterable[dict]) -> None:
    """Write records to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
