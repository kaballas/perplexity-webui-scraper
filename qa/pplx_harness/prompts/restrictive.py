"""Restrictive prompt template and builder."""

from collections import defaultdict
from typing import Any

from ..constants import (
    DEFAULT_CONSTRAINT_FILTER,
    DEFAULT_IN_SCOPE_MODULES,
    DEFAULT_MIN_ITEMS,
    DEFAULT_OBJECT_OF_ANALYSIS,
)

RESTRICTIVE_TEMPLATE = """
Instruction:
Think step by step INTERNALLY to identify only verified LIMITATIONS of the feature described in Context; DO NOT reveal your steps. Output must strictly follow Deliverable.

Context:
- Title: {title}
- Description: {description}
- Area: {area}
- Product: {product}

Scope:
- Object of analysis: {object_of_analysis}
- In-scope modules: {in_scope_modules}
- Constraint filter: {constraint_filter}
- Exclude: generic UX opinions, performance anecdotes, benefits, mitigations, workarounds, sales claims, and topics not directly constraining the object of analysis.

Rules (hard):
Allowed controls for "control" field in validation JSON:
["record-keeping","audit-trail","privacy","data-retention","equal-opportunity","merit-selection",
 "conflict-of-interest","notification-content","access-control","provenance","reporting-disclosure",
 "localization","jurisdiction-mapping","appeals-review","governance"].

1) Produce ONLY a numbered list starting at 1; one item per line; each item is a SINGLE factual sentence; no headers/preface/summary/citations/markdown.
2) Each item MUST explicitly state the system limitation AND how it constrains the object of analysis within the stated scope.
3) Include ONLY limitations that are documented or widely recognized in authoritative sources (product docs, admin guides, release notes, KBAs). No speculation.
4) Output AT LEAST {min_items} verified items if any exist; otherwise use the sentinel. Each item MUST include an authoritative evidence pointer (SAP Help/Support/KBA/Release Note/Implementation Guide URL or ID).
5) Controls must be one of the allowed list above.
6) After the numbered list, output a VALIDATION JSON object exactly in this format (no extra text):

{{"validation":[
  {{"item":1,"object":"<component>","module":"<module>","impact":"<short clause>","config_required":"yes|no","evidence_pointer":"<SAP Help/KBA URL or ID>","control":"<see allowed list>"}},
  {{"item":2,"object":"<component>","module":"<module>","impact":"<short clause>","config_required":"yes|no","evidence_pointer":"<SAP Help/KBA URL or ID>","control":"<see allowed list>"}}
]}}

7) If no verified, scope-specific limitations exist, output EXACTLY:
1. No verified limitations found within the specified scope.
{{"validation":[]}}

Deliverable:
1. <single-sentence limitation tied to the scope>
2. <single-sentence limitation tied to the scope>
...
{{"validation":[...]}}
"""


def safe_format(template: str, mapping: dict[str, Any]) -> str:
    """
    Format with defaults for missing keys.
    Any placeholder not provided resolves to empty string.
    """

    class SafeDict(defaultdict):
        def __missing__(self, key: str) -> str:
            return ""

    return template.format_map(SafeDict(str, mapping))


def build_restrictive_prompt(record: dict[str, Any]) -> str:
    """Inject record fields into the restrictive template with safe defaults."""
    title = record.get("Title", "Unknown Title")
    description = record.get("Description", "No description available")

    # Normalize list-ish fields
    area = record.get("Area", [])
    product = record.get("Product", [])
    area_str = ", ".join(area) if isinstance(area, list) else str(area)
    product_str = ", ".join(product) if isinstance(product, list) else str(product)

    # Accept multiple possible keys from upstream data; fall back to defaults
    obj = (
        record.get("ObjectOfAnalysis")
        or record.get("object_of_analysis")
        or DEFAULT_OBJECT_OF_ANALYSIS
    )
    mods = (
        record.get("InScopeModules")
        or record.get("in_scope_modules")
        or DEFAULT_IN_SCOPE_MODULES
    )
    filt = (
        record.get("ConstraintFilter")
        or record.get("constraint_filter")
        or DEFAULT_CONSTRAINT_FILTER
    )

    mapping = {
        "title": title,
        "description": description,
        "area": area_str,
        "product": product_str,
        "object_of_analysis": obj,
        "in_scope_modules": mods,
        "constraint_filter": filt,
        "min_items": DEFAULT_MIN_ITEMS,
    }
    return safe_format(RESTRICTIVE_TEMPLATE, mapping)


__all__ = ["RESTRICTIVE_TEMPLATE", "build_restrictive_prompt", "safe_format"]
