#!/usr/bin/env python3
"""
Utility script that probes the running Perplexity WebUI scraper API for the list
of available model identifiers. Since the server does not expose a dedicated
endpoint for the registry, we deliberately trigger a validation error on
``/ask`` and extract the model catalogue from the error message.
"""

from __future__ import annotations

import argparse
import sys
from typing import Iterable

import httpx
import re


def check_health(base_url: str, *, timeout: float = 10.0) -> None:
    """Raise an exception if the API health-check endpoint is unavailable."""

    url = f"{base_url.rstrip('/')}/health"
    response = httpx.get(url, timeout=timeout)
    response.raise_for_status()


def extract_models(detail_message: str) -> list[str] | None:
    """
    Parse the HTTP 422 detail string emitted by the API when an unknown model is
    supplied. The message contains the registry as a comma-separated list.
    """

    match = re.search(r"Available options:\s*(.+)", detail_message)
    if not match:
        return None

    options = match.group(1).rstrip(".")
    models = [item.strip() for item in options.split(",") if item.strip()]
    return models or None


def fetch_model_registry(base_url: str, *, timeout: float = 10.0) -> list[str]:
    """
    Submit an invalid ``model`` value to ``/ask`` in order to coax the API into
    returning the authoritative list of choices.
    """

    url = f"{base_url.rstrip('/')}/ask"
    payload = {"query": "model registry probe", "model": "__invalid_model__"}
    response = httpx.post(url, json=payload, timeout=timeout)

    if response.status_code != 422:
        raise RuntimeError(
            f"Unexpected status {response.status_code} from {url}; "
            "expected 422 Unprocessable Entity to extract model names."
        )

    data = response.json()
    detail = data.get("detail")
    if not isinstance(detail, str):
        raise RuntimeError("Response does not contain a textual 'detail' field.")

    models = extract_models(detail)
    if not models:
        raise RuntimeError("Failed to parse model registry from response message.")

    return models


def print_models(models: Iterable[str]) -> None:
    """Display the model identifiers, one per line."""

    for model in sorted(models):
        print(model)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List model registry exposed by the Perplexity WebUI scraper API."
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Root URL of the running API (default: %(default)s).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds for each request (default: %(default).1f).",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        check_health(args.base_url, timeout=args.timeout)
        models = fetch_model_registry(args.base_url, timeout=args.timeout)
    except httpx.HTTPError as exc:
        print(f"HTTP error while communicating with the API: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - top-level CLI guard
        print(f"Failed to retrieve model registry: {exc}", file=sys.stderr)
        return 1

    print_models(models)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
