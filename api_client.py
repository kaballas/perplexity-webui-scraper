"""
Command-line client for the Perplexity FastAPI service.

The script submits questions to the locally running API created in `perplexity_webui_scraper.api`
and prints the resulting answer (either as a single JSON blob or as streamed JSON lines).
"""

from __future__ import annotations

import argparse
import logging
import json
import sys
from os import getenv
from typing import Any

import httpx
from httpx import HTTPStatusError, RequestError, ResponseNotRead

from perplexity_webui_scraper import get_logger, set_debug_level
from perplexity_webui_scraper.logger import log_request_details, log_response_details


logger = get_logger("perplexity_webui_scraper.api_client")


def _sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive fields before logging."""
    sanitized = dict(payload)
    if sanitized.get("session_token"):
        sanitized["session_token"] = "[MASKED]"
    return sanitized


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "query": args.query,
        "model": args.model,
        "citation_mode": args.citation_mode,
        "search_focus": args.search_focus,
        "time_range": args.time_range,
        "language": args.language,
        "session_token": args.session_token or getenv("PERPLEXITY_SESSION_TOKEN"),
        "save_to_library": args.save_to_library,
    }

    if args.source_focus:
        payload["source_focus"] = args.source_focus if len(args.source_focus) > 1 else args.source_focus[0]

    if args.timezone:
        payload["timezone"] = args.timezone

    if args.coordinates:
        payload["coordinates"] = tuple(args.coordinates)

    if args.files:
        payload["files"] = args.files

    # Remove keys explicitly set to None so the API can fall back to defaults.
    filtered_payload = {key: value for key, value in payload.items() if value is not None}
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Prepared payload keys: %s", sorted(filtered_payload.keys()))
        logger.debug("Payload preview: %s", _sanitize_payload(filtered_payload))
    return filtered_payload


def run_once(base_url: str, payload: dict[str, Any], timeout: float | None) -> None:
    log_request_details(logger, "POST", f"{base_url}/ask", data=_sanitize_payload(payload))
    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        response = client.post("/ask", json=payload)
        response.raise_for_status()
        json_response = response.json()
        log_response_details(logger, response.status_code, response_data=json_response)
        print(json.dumps(json_response, indent=2, ensure_ascii=False))


def run_stream(base_url: str, payload: dict[str, Any], timeout: float | None) -> None:
    log_request_details(logger, "POST", f"{base_url}/ask/stream", data=_sanitize_payload(payload))
    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        with client.stream("POST", "/ask/stream", json=payload) as response:
            try:
                response.raise_for_status()
            except HTTPStatusError:
                # Consume the body so `response.text` becomes available to callers.
                response.read()
                raise
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    print(line, file=sys.stderr)
                    continue

                logger.debug("Received stream line: %s", line)
                print(json.dumps(data, ensure_ascii=False))
                if data.get("error"):
                    break


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI client for the Perplexity WebUI FastAPI server.",
    )
    parser.add_argument("query", help="The question or prompt to send.")
    parser.add_argument(
        "--base-url",
        default=getenv("PERPLEXITY_API_BASE_URL", "http://127.0.0.1:8000"),
        help="Base URL of the FastAPI service (default: %(default)s).",
    )
    parser.add_argument(
        "--session-token",
        help="Session token to forward to the API. Defaults to PERPLEXITY_SESSION_TOKEN environment variable.",
    )
    parser.add_argument(
        "--model",
        default="Best",
        help="Model name as accepted by the API (default: %(default)s).",
    )
    parser.add_argument(
        "--citation-mode",
        default="PERPLEXITY",
        help="Citation mode (PERPLEXITY, MARKDOWN, CLEAN).",
    )
    parser.add_argument(
        "--search-focus",
        default="WEB",
        help="Search focus (WEB, WRITING).",
    )
    parser.add_argument(
        "--source-focus",
        nargs="+",
        help="Optional source focus values (WEB, ACADEMIC, SOCIAL, FINANCE). Specify multiple for combined focus.",
    )
    parser.add_argument(
        "--time-range",
        default="ALL",
        help="Time range (ALL, TODAY, LAST_WEEK, LAST_MONTH, LAST_YEAR).",
    )
    parser.add_argument(
        "--language",
        default="en-US",
        help="Language code (default: %(default)s).",
    )
    parser.add_argument(
        "--timezone",
        help="Timezone string, e.g. 'America/New_York'.",
    )
    parser.add_argument(
        "--coordinates",
        nargs=2,
        type=float,
        metavar=("LAT", "LON"),
        help="Latitude and longitude to forward to the API.",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Optional list of file paths available to the API server.",
    )
    parser.add_argument(
        "--save-to-library",
        action="store_true",
        help="Forward save_to_library flag to the API.",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Use the streaming endpoint and emit JSON lines.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Optional HTTP timeout in seconds. Defaults to httpx's default.",
    )
    parser.add_argument(
        "--verbrose",
        action="store_true",
        help="Enable verbose client logging and debug output.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.verbrose:
        set_debug_level("perplexity_webui_scraper.api_client")
        logger.debug("--verbrose enabled; debug logging active.")

    payload = build_payload(args)

    try:
        if args.stream:
            run_stream(args.base_url, payload, args.timeout)
        else:
            run_once(args.base_url, payload, args.timeout)
    except HTTPStatusError as exc:
        detail = ""
        try:
            detail = exc.response.text
        except ResponseNotRead:
            detail = exc.response.read().decode("utf-8", errors="replace")
        print(f"API returned HTTP {exc.response.status_code}: {detail}", file=sys.stderr)
        return 1
    except RequestError as exc:
        print(f"Request to API failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
