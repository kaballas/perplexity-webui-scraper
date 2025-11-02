"""Sanitisation routines for model-produced limitation lists."""

from __future__ import annotations

import json
import re
from typing import Any, Tuple

from ..constants import ALLOWED_CONTROLS, SENTINEL_TEXT
from ..gating.enforce import enforce_topic_gate
from ..text.regexes import ITEM_RE, VALIDATION_JSON_RE
from ..text.sentences import first_sentence

__all__ = ["extract_validation_from_raw", "sanitize_limitations_output", "is_sentinel"]


def is_sentinel(text: str) -> bool:
    """Check whether the text matches the sentinel response."""
    normalised = re.sub(r"\s+", " ", (text or "")).strip().lower()
    return normalised == SENTINEL_TEXT.lower()


def _validate_controls(validation_obj: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    filtered: list[dict[str, Any]] = []
    if not isinstance(validation_obj, dict):
        return {"validation": filtered}

    rows = validation_obj.get("validation")
    if not isinstance(rows, list):
        return {"validation": filtered}

    for row in rows:
        if not isinstance(row, dict):
            continue
        control = str(row.get("control", "")).strip().lower()
        if control and control in ALLOWED_CONTROLS:
            filtered.append(row)

    return {"validation": filtered}


def extract_validation_from_raw(raw: str) -> Tuple[str, dict[str, list[dict[str, Any]]]]:
    """
    Remove and parse any trailing validation JSON block.
    Returns (text_without_json, validation_dict).
    """
    if not raw or not isinstance(raw, str):
        return raw or "", {"validation": []}

    match = VALIDATION_JSON_RE.search(raw)
    if not match:
        candidates = list(
            re.finditer(r'(\{.*"validation"\s*:\s*\[.*?\]\s*\})', raw, re.DOTALL)
        )
        if not candidates:
            return raw, {"validation": []}
        match = candidates[-1]

    json_part = match.group(1)
    try:
        parsed = json.loads(json_part)
    except Exception:
        return raw[: match.start(1)].strip(), {"validation": []}

    return raw[: match.start(1)].strip(), _validate_controls(parsed)


def _extract_numbered_items(raw_text: str) -> list[str]:
    items: list[str] = []
    for match in ITEM_RE.finditer(raw_text):
        candidate = match.group(2).strip()
        sentence = first_sentence(candidate)
        sentence = re.sub(r"\s+", " ", sentence).strip(" -;:,")
        if sentence:
            items.append(sentence)
    return items


def _fallback_items(raw_text: str) -> list[str]:
    items: list[str] = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^\d{1,2}[.)]\s+", "", line)
        sentence = first_sentence(line)
        sentence = re.sub(r"\s+", " ", sentence).strip(" -;:,")
        if sentence:
            items.append(sentence)
    return items


def sanitize_limitations_output(
    raw: str, description: str, min_items: int = 3, max_items: int = 12
) -> dict[str, Any]:
    """
    Enforce numbering, single-sentence items, gating, deduplication, and validation structure.
    Returns dict: {"text": "<numbered text>", "validation": {...}}.
    """
    text_part, validation_obj = extract_validation_from_raw(raw)

    if not text_part or not isinstance(text_part, str):
        return {"text": SENTINEL_TEXT, "validation": validation_obj}

    cleaned = text_part.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"\*|\-|�?�|�z�|�-�|�-�", "", cleaned)
    cleaned = re.sub(r"\[(?:\d+|[^\]]+)\]", "", cleaned)
    cleaned = cleaned.strip()

    items = _extract_numbered_items(cleaned)
    if not items:
        items = _fallback_items(cleaned)

    if not items:
        return {"text": SENTINEL_TEXT, "validation": validation_obj}

    gated = enforce_topic_gate(items, description)
    if not gated:
        return {"text": SENTINEL_TEXT, "validation": validation_obj}

    deduped: list[str] = []
    seen: set[str] = set()
    for sentence in gated:
        lowered = sentence.lower()
        if lowered not in seen:
            seen.add(lowered)
            deduped.append(sentence)

    if not deduped:
        return {"text": SENTINEL_TEXT, "validation": validation_obj}

    numbered = [f"{idx}. {text}" for idx, text in enumerate(deduped[:max_items], start=1)]
    final_text = "\n".join(numbered)
    return {"text": final_text, "validation": validation_obj}
