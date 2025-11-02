"""Processing pipeline for Perplexity harness records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Protocol

from ..constants import DEFAULT_MIN_ITEMS, SENTINEL_TEXT
from ..net.pplx import collect_stream_text
from ..net.rewriter import rewrite_human_readable, strip_validation_block
from ..prompts.restrictive import build_restrictive_prompt
from ..sanitize.limitations import sanitize_limitations_output
from ..types import PplxClient
from ..validate.records import validate_record

__all__ = ["PipelineCallbacks", "process_records", "process_single_record"]


class PanelContext(Protocol):
    def __enter__(self) -> Any: ...
    def __exit__(self, exc_type, exc, tb) -> None: ...


class PipelineCallbacks(Protocol):
    """Optional UI callbacks for pipeline progress."""

    def info(self, message: str) -> None: ...

    def warn(self, message: str) -> None: ...

    def err(self, message: str) -> None: ...

    def panel_status(self, title: str) -> PanelContext: ...


@dataclass(slots=True)
class _NoOpCallbacks:
    def info(self, message: str) -> None:  # pragma: no cover - trivial
        return

    def warn(self, message: str) -> None:  # pragma: no cover - trivial
        return

    def err(self, message: str) -> None:  # pragma: no cover - trivial
        return

    def panel_status(self, title: str) -> PanelContext:  # pragma: no cover - trivial
        class _Dummy:
            def __enter__(self_inner):
                return self_inner

            def __exit__(self_inner, exc_type, exc, tb):
                return False

        return _Dummy()


def process_single_record(
    record: dict[str, Any],
    index: int,
    total: int,
    client: PplxClient,
    *,
    callbacks: PipelineCallbacks | None = None,
    min_items: int = DEFAULT_MIN_ITEMS,
) -> dict[str, Any]:
    """Process a single record through prompt, sanitisation, rewrite, and validation."""
    cb = callbacks or _NoOpCallbacks()
    title = record.get("Title", "Unknown")
    cb.info(f"Processing record {index}/{total}: {title}")

    prompt = build_restrictive_prompt(record)
    final_result = SENTINEL_TEXT
    validation_obj: dict[str, Any] = {"validation": []}

    try:
        with cb.panel_status(f"Record {index}: Processing"):
            raw_answer = collect_stream_text(client, prompt)
        sanitized = sanitize_limitations_output(
            raw_answer,
            record.get("Description", ""),
            min_items=min_items,
        )
        final_result = sanitized.get("text") or final_result
        validation_obj = sanitized.get("validation", {"validation": []})
    except Exception as exc:
        cb.warn(f"Streaming failed for record {index}: {exc}; attempting fallback.")
        try:
            raw_answer = client.ask_once(prompt)
            sanitized = sanitize_limitations_output(
                raw_answer,
                record.get("Description", ""),
                min_items=min_items,
            )
            final_result = sanitized.get("text") or final_result
            validation_obj = sanitized.get("validation", {"validation": []})
        except Exception as fallback_exc:
            cb.err(f"Non-streaming fallback failed for record {index}: {fallback_exc}")
            final_result = SENTINEL_TEXT
            validation_obj = {"validation": []}

    enriched = dict(record)
    enriched["research_analysis"] = final_result
    enriched["validation"] = validation_obj

    numbered_only = strip_validation_block(final_result)
    try:
        enriched["human_readable"] = rewrite_human_readable(numbered_only)
    except Exception:
        enriched["human_readable"] = numbered_only

    validated = validate_record(enriched, min_items=min_items)
    return validated


def process_records(
    records: Iterable[dict[str, Any]],
    client: PplxClient,
    *,
    max_records: int | None = None,
    callbacks: PipelineCallbacks | None = None,
    min_items: int = DEFAULT_MIN_ITEMS,
) -> List[dict[str, Any]]:
    """Process multiple records, returning validated outputs."""
    cb = callbacks or _NoOpCallbacks()
    processed: List[dict[str, Any]] = []
    limited_records = list(records)
    if max_records is not None:
        limited_records = limited_records[:max_records]
    total = len(limited_records)
    cb.info(f"Processing {total} record(s)")
    for index, record in enumerate(limited_records, start=1):
        try:
            processed_record = process_single_record(
                record,
                index,
                total,
                client,
                callbacks=cb,
                min_items=min_items,
            )
            processed.append(processed_record)
            cb.info(f"Record {index} completed")
        except Exception as exc:
            cb.err(f"Error processing record {index}: {exc}")
    return processed
