"""Record-level validation utilities."""

from __future__ import annotations

import re
from typing import Any

from ..constants import ALLOWED_CONTROLS
from ..sanitize.limitations import is_sentinel
from .evidence import is_authoritative, normalize_module

__all__ = ["validate_record"]


def _extract_numbered_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if re.match(r"^\d+[.)]\s+", line)]


def validate_record(record: dict[str, Any], min_items: int = 3) -> dict[str, Any]:
    """
    Post-validation gate: enforce minimum item count, authoritative evidence, and row sanity.
    Mutates neither the input nor nested structures; returns a copy.
    """
    output = dict(record)
    raw_text = output.get("research_analysis") or ""
    text = raw_text.strip()
    validation_section = (
        output.get("validation") if isinstance(output.get("validation"), dict) else {"validation": []}
    )
    rows = validation_section.get("validation") if isinstance(validation_section.get("validation"), list) else []

    items = _extract_numbered_lines(text)
    sentinel = is_sentinel(raw_text)
    violations: list[str] = []

    if sentinel and rows:
        violations.append("sentinel_with_validation")

    if not sentinel and len(items) < min_items:
        violations.append(f"min_items<{min_items}")

    pruned_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        obj = (row.get("object") or "").strip()
        module = normalize_module(row.get("module"))
        control = (row.get("control") or "").strip().lower()
        impact = (row.get("impact") or "").strip()
        evidence = (row.get("evidence_pointer") or "").strip()
        evidence_ok = evidence and (is_authoritative(evidence) or evidence.lower().startswith("sap kba"))
        control_ok = control in ALLOWED_CONTROLS
        valid = bool(obj) and bool(module) and control_ok and evidence_ok and bool(impact)
        if valid:
            cleaned = dict(row)
            cleaned["module"] = module
            pruned_rows.append(cleaned)

    if not sentinel and len(pruned_rows) == 0:
        violations.append("missing_validation")

    if not sentinel and pruned_rows and len(pruned_rows) > len(items):
        violations.append("validation_count>items")

    validation_section["validation"] = pruned_rows
    output["validation"] = validation_section

    if sentinel:
        output["processed"] = not violations
    else:
        output["processed"] = (
            len(items) >= min_items and len(pruned_rows) == len(items) and not violations
        )

    output["metrics"] = {"items": len(items), "validation_rows": len(pruned_rows), "min_items": min_items}

    if violations:
        output["failure_reason"] = ",".join(violations)
    else:
        output.pop("failure_reason", None)
    return output
