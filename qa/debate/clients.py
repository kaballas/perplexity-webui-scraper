"""Clients for API interactions with different services."""

from __future__ import annotations

import sys
import time
import requests
from dataclasses import dataclass
from typing import Any

from generate_wricef_prompts import (
    DEFAULT_API_URL as DEFAULT_HUGGING_URL,
    DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
    DEFAULT_TEMPERATURE as DEFAULT_HUGGING_TEMPERATURE,
    ENV_TOKEN_KEY as HUGGING_TOKEN_ENV,
    ApiConfig as BaseApiConfig,
    call_wricef_api as base_call_wricef_api,
)
from pplx_harness.net.pplx import PplxAdapter, collect_stream_text


@dataclass(slots=True)
class ApiConfig:
    url: str
    token: str | None
    model: str
    temperature: float
    timeout: float
    include_raw: bool


class HuggingFaceClient:
    """Client for interacting with HuggingFace WRICEF API."""

    def __init__(self, config: ApiConfig):
        self.config = config

    def call_api(self, prompt: str) -> str:
        """Call the HuggingFace API with the given prompt."""
        print(f"[DEBUG] HuggingFaceClient: calling API with URL={self.config.url}, model={self.config.model}", file=sys.stderr)
        # Show first 100 characters of the prompt for debugging
        prompt_preview = prompt
        print(f"[DEBUG] HuggingFaceClient: prompt preview='{prompt_preview}'", file=sys.stderr)
        start_time = time.time()
        text, _ = base_call_wricef_api(prompt, config=self.config)
        elapsed = time.time() - start_time
        print(f"[DEBUG] HuggingFaceClient: API returned {len(text)} chars in {elapsed:.2f}s", file=sys.stderr)
        return text.strip()


class PerplexityClient:
    """Client for interacting with Perplexity API."""

    def __init__(self, session_token: str):
        self._client = PplxAdapter(session_token=session_token)

    def call_api(self, prompt: str) -> str:
        """Call the Perplexity API with the given prompt."""
        # Show first 100 characters of the prompt for debugging
        prompt_preview = prompt[:100] + "..." if len(prompt) > 100 else prompt
        print(f"[DEBUG] PerplexityClient: calling with prompt preview='{prompt_preview}'", file=sys.stderr)
        start_time = time.time()
        text = collect_stream_text(self._client, prompt)
        elapsed = time.time() - start_time
        print(f"[DEBUG] PerplexityClient: stream returned {len(text)} chars in {elapsed:.2f}s", file=sys.stderr)
        return text.strip()
