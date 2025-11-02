"""Sentence-level text helpers."""

import re

__all__ = ["first_sentence"]


ABBREVIATION_RE = re.compile(r"^[A-Z]\.$")


def first_sentence(text: str) -> str:
    """Extract the first sentence from text without breaking URLs or abbreviations."""
    txt = text.strip()
    for match in re.finditer(r"[.!?]", txt):
        end = match.end()
        candidate = txt[:end].strip()
        if not candidate:
            continue
        last_token = candidate.split()[-1]
        if last_token.startswith("http"):
            continue
        if ABBREVIATION_RE.match(last_token):
            continue
        return candidate
    return txt
