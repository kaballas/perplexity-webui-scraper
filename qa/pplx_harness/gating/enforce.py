"""Topic and compliance gating logic."""

from __future__ import annotations

from typing import Iterable

from .compliance import NEGATIVE_VERBS, is_compliance_tied
from .topics import classify_topic

WORKFLOW_TERMS = (
    "route map",
    "approval",
    "approver",
    "step",
    "stage",
    "notification",
    "operator",
    "rbp",
    "permission",
    "status",
    "field",
    "rule",
    "business rule",
    "template",
    "workflow",
)
IDENTIFIER_TERMS = (
    "identifier",
    "id",
    "external id",
    "key",
    "unique",
    "duplication",
    "collision",
    "mapping",
)
DEFAULTING_TERMS = (
    "default",
    "derive",
    "pre-populate",
    "propagate",
    "rule",
    "picklist",
    "position",
    "org unit",
    "job",
    "role description",
)
MANDATORY_TERMS = (
    "mandatory",
    "required",
    "validation",
    "error",
    "warning",
    "submit",
    "incomplete",
    "field",
)


def topic_gate(sentence: str, topics: Iterable[str]) -> bool:
    """Check whether a sentence matches the relevant topic signals."""
    lowered = sentence.lower()
    verbs_hit = any(verb in lowered for verb in NEGATIVE_VERBS)
    topic_set = set(topics)

    if "legislative" in topic_set and is_compliance_tied(sentence):
        return True

    if not topic_set:
        return verbs_hit

    topic_hits = (
        ("workflow" in topic_set and any(term in lowered for term in WORKFLOW_TERMS))
        or ("identifier" in topic_set and any(term in lowered for term in IDENTIFIER_TERMS))
        or ("defaulting" in topic_set and any(term in lowered for term in DEFAULTING_TERMS))
        or ("mandatory_fields" in topic_set and any(term in lowered for term in MANDATORY_TERMS))
    )
    return verbs_hit and topic_hits


def enforce_compliance_gate(items: list[str]) -> list[str]:
    """Filter items to those tied to compliance; fallback to empty list."""
    gated = [item for item in items if is_compliance_tied(item)]
    return gated or []


def enforce_topic_gate(items: list[str], description: str) -> list[str]:
    """Filter limitation items using topic signals derived from the description."""
    topics = classify_topic(description)
    gated = [sentence for sentence in items if topic_gate(sentence, topics)]
    if "legislative" in topics:
        return enforce_compliance_gate(gated)
    return gated


__all__ = ["enforce_compliance_gate", "enforce_topic_gate", "topic_gate"]
