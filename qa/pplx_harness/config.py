"""Configuration helpers for the Perplexity harness."""

from __future__ import annotations

import argparse
from os import getenv
from pathlib import Path
from typing import Sequence, Tuple

from dotenv import load_dotenv

from .net.pplx import PplxAdapter
from .types import PplxClient, RunConfig

__all__ = ["create_client", "load_env", "load_run_config", "resolve_paths"]


def load_env() -> None:
    """Load environment variables from .env files if present."""
    load_dotenv()


def resolve_paths(env_input: str | None, env_output: str | None) -> Tuple[Path, Path]:
    """Resolve input/output paths from environment overrides."""
    input_path = Path(env_input).expanduser() if env_input else Path("data/sap_question.jsonl")
    output_path = (
        Path(env_output).expanduser() if env_output else Path("data/sap_question_test.jsonl")
    )
    return input_path, output_path


def create_client(session_token: str) -> PplxClient:
    """Instantiate the Perplexity client adapter."""
    if not session_token:
        raise ValueError("PERPLEXITY_SESSION_TOKEN not set. Live API access is required.")
    return PplxAdapter(session_token=session_token)


def load_run_config(argv: Sequence[str] | None = None) -> RunConfig:
    """Parse CLI arguments and environment variables into a RunConfig."""
    env_input = (getenv("PPLX_INPUT") or "").strip() or None
    env_output = (getenv("PPLX_OUTPUT") or "").strip() or None
    env_max_records = (getenv("PPLX_MAX_RECORDS") or "").strip() or None

    try:
        default_max_records = int(env_max_records) if env_max_records else 500
    except ValueError:
        default_max_records = 500

    parser = argparse.ArgumentParser(
        description="Process sample records through the Perplexity test harness."
    )
    parser.add_argument("--input", type=Path, help="Path to input JSONL file.")
    parser.add_argument("--output", type=Path, help="Path to write processed JSONL results.")
    parser.add_argument(
        "--max-records", type=int, help="Limit number of records processed in this test run."
    )
    args = parser.parse_args(argv)

    input_path, output_path = resolve_paths(env_input, env_output)
    if args.input:
        input_path = args.input.expanduser()
    if args.output:
        output_path = args.output.expanduser()
    max_records = args.max_records if args.max_records is not None else default_max_records

    session_token = (getenv("PERPLEXITY_SESSION_TOKEN") or "").strip()
    client = create_client(session_token)
    return RunConfig(
        input_path=input_path,
        output_path=output_path,
        max_records=max_records,
        client=client,
    )
