"""Topic classification helpers."""

from __future__ import annotations

TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "legislative": (
        "legislation",
        "legislative",
        "statutory",
        "public service act",
        "award",
        "enterprise agreement",
        "directive",
        "policy",
        "policies",
        "compliance",
    ),
    "workflow": (
        "workflow",
        "approval",
        "approvals",
        "route map",
        "routing",
        "endorsement",
        "teaching",
        "non-teaching",
        "hr business partner",
    ),
    "identifier": (
        "unique identifier",
        "unique id",
        "requisition id",
        "job id",
        "req id",
        "identifier",
    ),
    "defaulting": (
        "default",
        "auto default",
        "pre-populate",
        "prepopulate",
        "organisational unit",
        "org unit",
        "job",
        "position",
        "role description",
    ),
    "mandatory_fields": (
        "mandatory",
        "required field",
        "validation",
        "error message",
        "warning",
        "incomplete",
        "submission",
        "submit",
    ),
}


def classify_topic(description: str) -> set[str]:
    """Return a set of topics triggered by keywords in the description."""
    lowered = (description or "").lower()
    flags = {topic for topic, kws in TOPIC_KEYWORDS.items() if any(k in lowered for k in kws)}
    return flags


__all__ = ["TOPIC_KEYWORDS", "classify_topic"]
