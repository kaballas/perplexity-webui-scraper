"""Compiled regular expressions used across the harness."""

import re

VALIDATION_JSON_RE = re.compile(
    r'(\{\s*"validation"\s*:\s*\[.*?\]\s*\})\s*\Z', re.DOTALL
)
ITEM_RE = re.compile(
    r"^\s*(\d{1,2})[.)]\s+(.*?)(?=(?:\n\s*\d{1,2}[.)]\s)|\Z)", re.DOTALL | re.MULTILINE
)

__all__ = ["ITEM_RE", "VALIDATION_JSON_RE"]
