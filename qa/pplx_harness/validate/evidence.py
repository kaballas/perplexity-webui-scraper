"""Evidence validation helpers."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from ..constants import ALLOWED_MODULES_ORDERED, AUTHORITATIVE_SUFFIXES

__all__ = ["is_authoritative", "normalize_module"]

_NORMALIZATION_TOKENS = sorted(ALLOWED_MODULES_ORDERED, key=len, reverse=True)


def is_authoritative(url: str) -> bool:
    """Return True when the URL belongs to an allowed authoritative domain."""
    try:
        netloc = urlparse(url).netloc.lower().rstrip(".")
        host = netloc.split("@")[-1]
        host_only = host.split(":")[0]
        return any(
            host_only == suffix or host_only.endswith(suffix) for suffix in AUTHORITATIVE_SUFFIXES
        )
    except Exception:
        return False


def normalize_module(value: str | None) -> str:
    """Resolve various module spellings into the canonical label."""
    lowered = (value or "").strip().lower()
    for token in _NORMALIZATION_TOKENS:
        pattern = rf"(?<!\w){re.escape(token.lower())}(?!\w)"
        if re.search(pattern, lowered):
            return token
    return ""
