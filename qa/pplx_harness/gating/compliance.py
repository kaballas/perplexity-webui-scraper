"""Compliance gating helpers."""

COMPLIANCE_TERMS = (
    "compliance",
    "legislation",
    "legislative",
    "statutory",
    "evidence",
    "audit",
    "record",
    "retention",
    "privacy",
    "equal opportunity",
    "merit",
    "disclosure",
    "appeal",
    "governance",
    "policy",
    "directive",
    "act",
    "award",
    "agreement",
    "provenance",
    "access control",
    "consent",
)

NEGATIVE_VERBS = (
    "cannot",
    "does not",
    "no ",
    "limits",
    "restrict",
    "missing",
    "lack",
    "lacks",
    "prevents",
    "risks",
    "fails",
    "disabled",
    "unsupported",
)


def is_compliance_tied(sentence: str) -> bool:
    """Whether the sentence addresses compliance constraints with negative framing."""
    lowered = sentence.lower()
    return any(term in lowered for term in COMPLIANCE_TERMS) and any(
        verb in lowered for verb in NEGATIVE_VERBS
    )


__all__ = ["COMPLIANCE_TERMS", "is_compliance_tied", "NEGATIVE_VERBS"]
