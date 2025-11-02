"""CLI entrypoint orchestrating the Perplexity harness workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import config
from .io.jsonl import ensure_sample_input, read_jsonl, write_jsonl
from .processing.pipeline import PipelineCallbacks, process_records
from .ui import console


@dataclass(slots=True)
class _ConsoleCallbacks(PipelineCallbacks):
    def info(self, message: str) -> None:
        console.info(message)

    def warn(self, message: str) -> None:
        console.warn(message)

    def err(self, message: str) -> None:
        console.err(message)

    def panel_status(self, title: str):
        return console.panel_status(title)


def main() -> None:
    """Main entrypoint invoked by ``python -m pplx_harness``."""
    config.load_env()
    run_config = config.load_run_config()

    console.info(f"Input file: {run_config.input_path}")
    console.info(f"Output file: {run_config.output_path}")

    if not run_config.input_path.exists():
        console.warn("Input not found. Creating example JSONL.")
        ensure_sample_input(run_config.input_path)

    try:
        records = read_jsonl(run_config.input_path, limit=run_config.max_records)
    except Exception as exc:
        console.err(f"Error reading input file: {exc}")
        return

    callbacks: PipelineCallbacks = _ConsoleCallbacks()
    processed = process_records(
        records,
        run_config.client,
        max_records=run_config.max_records,
        callbacks=callbacks,
    )

    write_jsonl(run_config.output_path, processed)
    console.info(
        f"Test completed! {len(processed)} records processed and saved to {run_config.output_path}"
    )
    console.warn("Verify the output format before running a full batch.")
