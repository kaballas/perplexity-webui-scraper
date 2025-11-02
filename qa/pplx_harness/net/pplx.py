"""Perplexity Web UI client adapter and streaming utilities."""

from __future__ import annotations

from typing import Iterable, Optional

from perplexity_webui_scraper import (
    CitationMode,
    ModelType,
    Perplexity,
    SearchFocus,
    SourceFocus,
    TimeRange,
)

from ..types import PplxClient

__all__ = ["PplxAdapter", "collect_stream_text"]


def _extract_text_from_chunk(chunk: object) -> str:
    """
    Safely extract incremental text from a stream chunk.
    Tries common attributes in priority order.
    """
    for attr in ("delta", "text", "content", "message"):
        value = getattr(chunk, attr, None)
        if isinstance(value, str):
            return value

    try:
        choices = getattr(chunk, "choices", None)
        if choices and isinstance(choices, list):
            part = choices[0]
            for nested_attr in ("delta", "message", "content"):
                candidate = getattr(part, nested_attr, None)
                if isinstance(candidate, str):
                    return candidate
                if isinstance(candidate, dict):
                    content = candidate.get("content")
                    if isinstance(content, str):
                        return content
    except Exception:
        return ""

    return ""


class PplxAdapter(PplxClient):
    """Thin wrapper over ``Perplexity`` providing the protocol surface."""

    def __init__(self, session_token: str) -> None:
        self._client = Perplexity(session_token=session_token)

    def _ask(self, prompt: str):
        return self._client.ask(
            query=prompt,
            files=None,
            citation_mode=CitationMode.PERPLEXITY,
            model=ModelType.Best,
            save_to_library=False,
            search_focus=SearchFocus.WEB,
            source_focus=SourceFocus.WEB,
            time_range=TimeRange.ALL,
            language="en-US",
            timezone=None,
            coordinates=None,
        )

    def ask_stream(self, prompt: str) -> Iterable[object]:
        """Return a streaming iterator for the prompt response."""
        return self._ask(prompt).stream()

    def ask_once(self, prompt: str) -> str:
        """Return a single response for the prompt."""
        response = self._ask(prompt)
        answer = getattr(response, "answer", None)
        if isinstance(answer, str) and answer.strip():
            return answer
        candidates = [
            getattr(response, "text", None),
            getattr(response, "content", None),
        ]
        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                return candidate
        return ""


def collect_stream_text(client: PplxClient, prompt: str) -> str:
    """
    Consume a streaming response, assembling incremental text with fallback to final answer.
    """
    streamed = ""
    final_answer: Optional[str] = None
    for chunk in client.ask_stream(prompt):
        incremental = _extract_text_from_chunk(chunk)
        if incremental:
            streamed += incremental
        if getattr(chunk, "last_chunk", False):
            answer = getattr(chunk, "answer", None)
            if isinstance(answer, str) and answer.strip():
                final_answer = answer
    return final_answer if isinstance(final_answer, str) and final_answer.strip() else streamed
