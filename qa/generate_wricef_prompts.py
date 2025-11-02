"""CLI utility to generate WRICEF prompts and optionally fetch completions."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Optional, Set
import time
import requests
from typing import Any
import requests
import random
from pplx_harness.prompts import build_wricef_prompt

DEFAULT_API_URL = "https://kaballas-doe-tender.hf.space/api/v1/openai/chat/completions"
DEFAULT_MODEL = "_work"
DEFAULT_TEMPERATURE = 0.7
ENV_TOKEN_KEY = "WRICEF_API_TOKEN"


class RecordFormatError(TypeError):
    """Raised when input JSON records are not dictionaries."""


def _ensure_records(data: Any) -> List[dict[str, Any]]:
    """Normalise JSON payload into a list of dictionaries."""
    if isinstance(data, dict):
        if data and all(isinstance(v, list) for v in data.values()):
            flattened: List[dict[str, Any]] = []
            for group, items in data.items():
                for idx, item in enumerate(items, start=1):
                    if not isinstance(item, dict):
                        raise RecordFormatError(
                            f"Group '{group}' item {idx} is not an object; found {type(item).__name__}"
                        )
                    enriched = dict(item)
                    if "section" not in enriched and "Section" not in enriched:
                        enriched["section"] = group
                    flattened.append(enriched)
            return flattened
        return [dict(data)]
    if isinstance(data, list):
        records: List[dict[str, Any]] = []
        for idx, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                raise RecordFormatError(
                    f"Record {idx} is not an object; found {type(item).__name__}"
                )
            records.append(item)
        return records
    raise RecordFormatError(f"Unsupported JSON root type: {type(data).__name__}")


def _load_jsonl(text: str) -> List[dict[str, Any]]:
    """Parse newline-delimited JSON into a list of dictionaries."""
    records: List[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_no}: {exc}") from exc
        if not isinstance(parsed, dict):
            raise RecordFormatError(
                f"JSONL line {line_no} is not an object; found {type(parsed).__name__}"
            )
        records.append(parsed)
    return records


def load_records(path: Path) -> List[dict[str, Any]]:
    """Load records from a JSON or JSONL file."""
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return []
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        return _load_jsonl(text)
    data = json.loads(text)
    return _ensure_records(data)


def _record_key(record: dict[str, Any]) -> Optional[str]:
    """Derive a stable identifier for a record, prioritising explicit IDs."""
    key_candidates = (
        "wricef_record_key",
        "id",
        "ID",
        "external_id",
        "ExternalID",
        "requirement_id",
        "RequirementID",
        "requirement",
        "Requirement",
        "Title",
        "title",
    )
    for candidate in key_candidates:
        value = record.get(candidate)
        if isinstance(value, str):
            trimmed = value.strip()
            if trimmed:
                return trimmed
    return None


def _load_existing(path: Path) -> List[dict[str, Any]]:
    """Load existing results from disk if present."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return []
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        records: List[dict[str, Any]] = []
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSONL in existing output at line {line_no}: {exc}"
                ) from exc
            if isinstance(parsed, dict):
                records.append(parsed)
        return records
    data = json.loads(text)
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _normalise_for_prompt(record: dict[str, Any]) -> dict[str, Any]:
    """Inject fallback fields so build_wricef_prompt receives rich context."""
    normalised = dict(record)
    title = (
        normalised.get("Title")
        or normalised.get("title")
        or normalised.get("requirement")
        or normalised.get("Requirement")
        or normalised.get("name")
        or "Unspecified requirement"
    )
    description = (
        normalised.get("Description")
        or normalised.get("description")
        or normalised.get("response")
        or normalised.get("comment")
        or normalised.get("research_instructions")
        or normalised.get("requirement")
        or "No description provided."
    )
    stakeholders = (
        normalised.get("Stakeholders")
        or normalised.get("stakeholders")
        or normalised.get("owners")
        or normalised.get("owner")
    )
    if stakeholders:
        normalised["Stakeholders"] = stakeholders
    normalised["Title"] = title
    normalised["Description"] = description
    if "Project" not in normalised and "Program" not in normalised:
        if "project" in normalised:
            normalised["Project"] = normalised["project"]
        elif "program" in normalised:
            normalised["Project"] = normalised["program"]
    return normalised


def build_prompts(records: Iterable[dict[str, Any]]) -> List[str]:
    """Build WRICEF prompts for each record."""
    prompts: List[str] = []
    for record in records:
        prompts.append(build_wricef_prompt(_normalise_for_prompt(record)))
    return prompts


def build_review_prompt(record: dict[str, Any]) -> str:
    """Create a review instruction using the persisted WRICEF record."""
    review_payload = {
        key: value
        for key, value in record.items()
        if key not in {"wricef_review", "wricef_review_prompt", "wricef_review_raw", "wricef_review_error"}
    }
    record_json = json.dumps(review_payload, indent=2, ensure_ascii=False)
    return (
        "Instruction:\n"
        "Act as an SAP Solution architect performing a quality assurance and rewrite review of the WRICEF deliverable set below.\n"
        "Assess whether the numbered list and JSON comply with WRICEF governance, gating rules, and formatting expectations.\n"
        "If issues exist, explain them and provide corrected deliverables; if the solution is sound, confirm acceptance and restate the validated output verbatim.\n\n"
        "Record Under Review (JSON):\n"
        f"{record_json}\n\n"
        "Review Output Requirements:\n"
        "return only in json {id,requirement,wricef_details,how_to,big_rock_enhancement,issue}\n"
    )


@dataclass(slots=True)
class ApiConfig:
    url: str
    token: str | None
    model: str
    temperature: float
    timeout: float
    include_raw: bool




def call_wricef_api(
    prompt: str,
    *,
    config,
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    retry_on_404: bool = False,
) -> tuple[str, dict[str, Any]]:
    """Send prompt to WRICEF completion API with retry logic and return content plus raw JSON.

    Retries:
      - Network/timeout errors (requests.exceptions.RequestException)
      - HTTP 5xx
      - HTTP {408, 425, 429} always
      - HTTP 404 only when retry_on_404=True
    Backoff: exponential with small jitter.
    """
    headers = {
        "accept": "*/*",
        "Content-Type": "application/json",
    }
    if getattr(config, "token", None):
        headers["Authorization"] = f"Bearer {config.token}"

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "model": config.model,
        "stream": False,
        "temperature": config.temperature,
    }

    base_retry_statuses = {408, 425, 429}
    if retry_on_404:
        base_retry_statuses.add(404)

    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                config.url,
                headers=headers,
                json=payload,
                timeout=getattr(config, "timeout", None),
            )

            status = response.status_code
            if status in base_retry_statuses or 500 <= status < 600:
                raise requests.HTTPError(f"Retryable HTTP error {status}", response=response)

            # For non-retryable HTTP errors, raise immediately.
            response.raise_for_status()

            data = response.json()
            try:
                content = data["choices"][0]["message"]["content"]
            except (KeyError, IndexError, TypeError) as exc:
                # Treat schema errors as non-retryable: caller must inspect upstream/system.
                raise ValueError("Unexpected API response structure") from exc

            return content, data if getattr(config, "include_raw", False) else {}

        except requests.exceptions.RequestException as exc:
            # Network/timeout or explicit HTTPError above.
            last_exc = exc
            if attempt < max_retries:
                delay = backoff_factor * (2 ** (attempt - 1))
                delay += random.uniform(0, delay * 0.1)  # jitter up to 10%
                time.sleep(delay)
                continue
            raise



def _reset_review_fields(record: dict[str, Any]) -> None:
    """Remove review-related fields prior to re-running a review."""
    for field in (
        "wricef_review",
        "wricef_review_prompt",
        "wricef_review_raw",
        "wricef_review_error",
    ):
        record.pop(field, None)


def _review_tracking_key(record: dict[str, Any]) -> str:
    """Return the key used to determine whether a record needs review."""
    key = record.get("wricef_record_key") or _record_key(record)
    if key:
        return key
    index = record.get("wricef_index")
    return f"wricef_index:{index}" if index is not None else "unknown"


def process_records(
    records: Iterable[dict[str, Any]],
    prompts: Iterable[str],
    *,
    api_config: ApiConfig | None,
    start_index: int = 1,
) -> List[dict[str, Any]]:
    """Attach prompts (and optional completions) to the original records."""
    results: List[dict[str, Any]] = []
    for idx, (record, prompt) in enumerate(
        zip(records, prompts, strict=True), start=start_index
    ):
        enriched = dict(record)
        enriched["wricef_prompt"] = prompt
        key = _record_key(record)
        if key:
            enriched["wricef_record_key"] = key
        if api_config and api_config.token:
            try:
                completion, raw = call_wricef_api(prompt, config=api_config)
                enriched["wricef_completion"] = completion
                if api_config.include_raw and raw:
                    enriched["wricef_completion_raw"] = raw
            except Exception as exc:
                enriched["wricef_completion_error"] = str(exc)
        results.append(enriched | {"wricef_index": idx})
    return results


def write_output(path: Path, records: List[dict[str, Any]]) -> None:
    """Persist enriched records to disk."""
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        lines = [json.dumps(record, ensure_ascii=False) for record in records]
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    else:
        path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")


def _format_stdout(records: List[dict[str, Any]]) -> str:
    """Return human-friendly output for console display."""
    parts: List[str] = []
    for record in records:
        idx = record.get("wricef_index", "?")
        parts.append(f"--- Record {idx} ---")
        prompt = record.get("wricef_prompt", "").strip()
        if prompt:
            parts.append(prompt)
        completion = record.get("wricef_completion")
        if completion:
            parts.append("")
            parts.append("Response:")
            parts.append(completion.strip())
        parts.append("")
    return "\n".join(parts).rstrip() + ("\n" if records else "")


def _build_api_config(args: argparse.Namespace) -> ApiConfig | None:
    token = args.api_token or os.getenv(ENV_TOKEN_KEY, "").strip()
    if not token and not args.allow_anonymous:
        return None
    return ApiConfig(
        url=args.api_url,
        token=token or None,
        model=args.model,
        temperature=args.temperature,
        timeout=args.timeout,
        include_raw=args.include_raw,
    )


def perform_review(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.output is None:
        parser.error("--review-index requires --output to locate the source records.")
    if not args.output.exists():
        parser.error(
            f"Cannot review records; output file '{args.output}' not found."
        )

    existing_records = _load_existing(args.output)
    if not existing_records:
        parser.error(f"No existing records found in '{args.output}'.")

    api_config = _build_api_config(args)
    if not api_config or not api_config.token:
        parser.error(
            "--review-index requires API access. Provide --api-token or set WRICEF_API_TOKEN."
        )

    def review_single(record: dict[str, Any]) -> None:
        review_prompt = build_review_prompt(record)
        _reset_review_fields(record)
        tracking_key = _review_tracking_key(record)
        record["wricef_review_prompt"] = review_prompt
        record["wricef_review_record_key"] = tracking_key
        try:
            review_completion, raw = call_wricef_api(review_prompt, config=api_config)
            record["wricef_review"] = review_completion
            if api_config.include_raw and raw:
                record["wricef_review_raw"] = raw
            record.pop("wricef_review_error", None)
        except Exception as exc:  # pragma: no cover - defensive
            record.pop("wricef_review", None)
            record.pop("wricef_review_raw", None)
            record["wricef_review_error"] = str(exc)

    if args.review_index == 0:
        processed = 0
        for record in existing_records:
            tracking_key = _review_tracking_key(record)
            already_reviewed = (
                record.get("wricef_review")
                and not record.get("wricef_review_error")
                and record.get("wricef_review_record_key") == tracking_key
            )
            if already_reviewed:
                continue
            review_single(record)
            processed += 1
        if processed == 0:
            print(
                "No records required review; all existing entries already include review results.",
                file=sys.stderr,
            )
            return 0
        existing_records.sort(key=lambda row: row.get("wricef_index", 0))
        write_output(args.output, existing_records)
        print(f"Review stored for {processed} record(s).")
        return 0

    target = next(
        (row for row in existing_records if row.get("wricef_index") == args.review_index),
        None,
    )
    if target is None:
        parser.error(f"wricef_index {args.review_index} not found in {args.output}.")

    review_single(target)
    existing_records.sort(key=lambda row: row.get("wricef_index", 0))
    write_output(args.output, existing_records)
    if "wricef_review_error" in target:
        print(
            f"Review stored with error for wricef_index {args.review_index}: {target['wricef_review_error']}",
            file=sys.stderr,
        )
    else:
        print(f"Review stored for wricef_index {args.review_index}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate WRICEF prompt(s) from JSON/JSONL input and optionally call the completion API."
    )
    parser.add_argument("input", type=Path, help="Path to JSON or JSONL records.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write enriched records (JSON or JSONL). Defaults to stdout.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip input records whose IDs already exist in the output file (requires --output).",
    )
    parser.add_argument(
        "--reprocess-index",
        type=int,
        help="Reprocess a single WRICEF record by its wricef_index (requires --output).",
    )
    parser.add_argument(
        "--review-index",
        type=int,
        help="Request a WRICEF QA review for stored records by wricef_index (use 0 to review all unreviewed records; requires --output).",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        help="Limit the number of records processed from the input file.",
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=f"Completion API endpoint (default: {DEFAULT_API_URL}).",
    )
    parser.add_argument(
        "--api-token",
        help=f"API token (overrides {ENV_TOKEN_KEY} environment variable).",
    )
    parser.add_argument(
        "--allow-anonymous",
        action="store_true",
        help="Permit running without an API token (skips completion requests).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model identifier for the API (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"Sampling temperature (default: {DEFAULT_TEMPERATURE}).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="HTTP timeout in seconds (default: 60).",
    )
    parser.add_argument(
        "--include-raw",
        action="store_true",
        help="Include raw API response JSON in output (warning: large).",
    )
    args = parser.parse_args(argv)

    if args.review_index is not None:
        if args.reprocess_index is not None:
            parser.error("--review-index cannot be combined with --reprocess-index.")
        if args.resume:
            parser.error("--review-index cannot be combined with --resume.")
        if args.max_records not in (None, 0):
            parser.error("--review-index cannot be combined with --max-records.")
        return perform_review(args, parser)

    records = load_records(args.input)
    existing_records: List[dict[str, Any]] = []
    existing_keys: Set[str] = set()

    if args.resume or args.reprocess_index is not None:
        if not args.output:
            parser.error("--resume/--reprocess-index requires --output to be specified.")
        if args.output.exists():
            existing_records = _load_existing(args.output)
            existing_keys = {
                key for row in existing_records if (key := _record_key(row)) is not None
            }
        else:
            if args.reprocess_index is not None:
                parser.error(
                    f"Cannot reprocess index {args.reprocess_index}; output file '{args.output}' not found."
                )
            print(
                f"Resume requested but output file '{args.output}' not found. Starting fresh.",
                file=sys.stderr,
            )

    start_index = len(existing_records) + 1

    if args.reprocess_index is not None:
        if not existing_records:
            parser.error(
                "Cannot reprocess without existing output records. Run without --reprocess-index first."
            )
        target = next(
            (row for row in existing_records if row.get("wricef_index") == args.reprocess_index),
            None,
        )
        if target is None:
            parser.error(
                f"wricef_index {args.reprocess_index} not found in {args.output}."
            )
        target_key = target.get("wricef_record_key") or _record_key(target)
        if not target_key:
            parser.error(
                f"Record at wricef_index {args.reprocess_index} has no identifiable key; cannot reprocess."
            )
        matching_records = [
            record for record in records if _record_key(record) == target_key
        ]
        if not matching_records:
            parser.error(
                f"Input does not contain a record matching key '{target_key}'."
            )
        records = matching_records
        existing_records = [
            row
            for row in existing_records
            if row.get("wricef_index") != args.reprocess_index
        ]
        existing_keys.discard(target_key)
        start_index = args.reprocess_index
    elif args.resume and existing_keys:
        records = [
            record
            for record in records
            if (key := _record_key(record)) is None or key not in existing_keys
        ]

    if args.max_records is not None and args.max_records >= 0 and args.reprocess_index is None:
        records = records[: args.max_records]

    prompts = build_prompts(records)

    api_config = _build_api_config(args)
    enriched = process_records(
        records,
        prompts,
        api_config=api_config,
        start_index=start_index,
    )

    combined = existing_records + enriched if existing_records else enriched
    if combined:
        combined.sort(key=lambda row: row.get("wricef_index", 0))

    if args.output:
        write_output(args.output, combined)
    else:
        print(_format_stdout(combined), end="")

    if args.resume and not enriched:
        print("No new records to process.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
