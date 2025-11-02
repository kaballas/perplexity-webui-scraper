"""WRICEF prompt template and builder."""

from typing import Any, Iterable

from .restrictive import safe_format

DEFAULT_WRICEF_COMPONENTS = (
    "Workflow, Reports, Interfaces, Conversions, Enhancements, Forms"
)

WRICEF_TEMPLATE = """
Instruction:
Serve as an SAP program architect to assess the necessity of WRICEF deliverables.
Begin with a concise checklist (3-7 bullets) of what you will do; keep items conceptual, not implementation-level.

Gating Checklist (execute sequentially before proposing any WRICEF items):
1) Evaluate whether SAP SuccessFactors standard configuration, administrative tools, or delivered content can fully satisfy the requirement without any custom code, bespoke integrations, data conversions, enhancements, or custom forms.
2) If standard configuration is adequate, halt immediately and return the sentinel required by rule 7: a single numbered line followed by an empty JSON object. In addition, provide a concise, step-by-step 'How to' guide outlining how to implement the requirement using standard configuration. Do not create or suggest WRICEF content unnecessarily.
3) Only proceed if standard configuration is insufficient and non-standard development is essential. Each WRICEF line must reference the specific custom artifact and articulate the configuration limitation that mandates a non-standard solution.

Reference Guidance:
- Workflow (W): For routing or approval processes unattainable by the delivered workflow designer.
- Report (R): If analytic needs are unmet by delivered Report Stories, ORD, or standard tiles.
- Interface (I): For new integration flows not supported by existing connectors or flat-file exports.
- Conversion (C): When data migration or historical loads need custom tools.
- Enhancement (E): For logic, extensions, or UI requirements beyond what business rules or MDF can provide.
- Form (F): For generated documents or signature flows that standard templates cannot accommodate.

Context:
- Requirement title: {title}
- Requirement summary: {description}
- Project / program: {project}
- Business process: {business_process}
- Landscape / modules: {landscape}
- Priority: {priority}
- Stakeholders: {stakeholders}
- Integration points: {integrations}
- Assumptions: {assumptions}
- Known dependencies: {dependencies}

Scope:
- WRICEF components in focus: {wricef_components}
- Target release window: {timeline}
- Compliance / quality notes: {quality_notes}
- Non-functional constraints: {constraints}

Deliverable Rules:
1) If halted at checklist step 2, output only the sentinel as described in rule 7, followed immediately by a stepwise 'How to' guide for implementing the requirement using standard SAP SuccessFactors configuration and tools. The 'How to' guide should be concise (3-7 steps) and solution-focused.
2) If required, list WRICEF components in a numbered list (starting from 1) using the following format:
   <Component>: <solution title> - <purpose> (Source -> Target) [Complexity: low|medium|high; Owner: <team or role>; Timeline: <milestone>]
3) Clearly document the non-standard artifact, articulate the configuration gap, and list key integrations/data flows for each item.
4) After the list, output the WRICEF JSON exactly as specified (no extra text):

{{"wricef_summary":[
  {{"item":1,"component":"Workflow","solution":"<short title>","purpose":"<concise goal>","source":"<system>","target":"<system>","owner":"<team/role>","complexity":"low|medium|high","timeline":"<milestone>","dependencies":["..."]}}
]}}

5) Exclude any out-of-scope components from both the list and the JSON output.
6) All evidence must be justifiable to delivery and architecture leads; do not fabricate justifications.
7) If no WRICEF items are necessary, output exactly:
1. No WRICEF components required for this requirement.
{{"wricef_summary":[]}}

Immediately following this, provide the 'How to' guide as specified above.

After generating WRICEF items or the sentinel, validate that all mandatory fields and output schemas have been met. If any required field is missing or the format does not precisely match the schema, revise before completing.

Output Format:
- For WRICEF items, first output the numbered list as above, then on a new line provide the following JSON object:
{{"wricef_summary": [
  {{"item": <integer>, "component": <string>, "solution": <string>, "purpose": <string>, "source": <string>, "target": <string>, "owner": <string>, "complexity": <"low"|"medium"|"high">, "timeline": <string>, "dependencies": [<string>, ...]}}
]}}

- For multiple components, increment the 'item' value for each entry within the 'wricef_summary' array. Maintain the key order as shown in the schema.
- Use only the fields specified. Do not add any extra fields to the JSON output.
- For any placeholder field (e.g., {{title}}, {{description}}) that is missing or empty, use an empty string ('') for string fields or an empty array ([]) for array fields (such as dependencies).
- Always include all fields in every object in the listed order; do not omit fields even if the value is blank or empty.
- The sentinel output (no WRICEF required) must be exactly:
1. No WRICEF components required for this requirement.
{{"wricef_summary":[]}}

- Immediately following, output a 3-7 step 'How to' guide for implementing the requirement with standard configuration.
"""


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        return ", ".join(str(item) for item in value)
    return str(value)


def build_wricef_prompt(record: dict[str, Any]) -> str:
    """Inject record fields into the WRICEF template with resilient defaults."""
    mapping = {
        "title": record.get("Title", "Unspecified requirement"),
        "description": record.get("Description", "No description provided."),
        "project": record.get("Project") or record.get("Program") or "Not supplied",
        "business_process": _stringify(
            record.get("BusinessProcess") or record.get("ProcessArea") or "Not supplied"
        ),
        "landscape": _stringify(
            record.get("Landscape")
            or record.get("Modules")
            or record.get("Systems")
            or "Not supplied"
        ),
        "priority": record.get("Priority", "Not ranked"),
        "stakeholders": _stringify(
            record.get("Stakeholders") or record.get("Owners") or "Not listed"
        ),
        "integrations": _stringify(
            record.get("IntegrationPoints") or record.get("Interfaces") or "None noted"
        ),
        "assumptions": _stringify(record.get("Assumptions") or "None provided"),
        "dependencies": _stringify(record.get("Dependencies") or "None documented"),
        "wricef_components": _stringify(
            record.get("WRICEFComponents") or DEFAULT_WRICEF_COMPONENTS
        ),
        "timeline": record.get("Timeline") or record.get("ReleaseWindow") or "Unscheduled",
        "quality_notes": _stringify(
            record.get("QualityNotes") or record.get("ComplianceNotes") or "None provided"
        ),
        "constraints": _stringify(
            record.get("Constraints") or record.get("NonFunctional") or "None provided"
        ),
    }
    return safe_format(WRICEF_TEMPLATE, mapping)


__all__ = ["WRICEF_TEMPLATE", "build_wricef_prompt"]
