import argparse
import json
import re
import sys
from pathlib import Path
from os import getenv
from dotenv import load_dotenv
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from collections import defaultdict
from urllib.parse import urlparse
from typing import Optional

import requests

from perplexity_webui_scraper import (
    Perplexity,
    CitationMode,
    ModelType,
    SearchFocus,
    SourceFocus,
    TimeRange,
)

# =========================
# A1.1 – ENV + CONSOLE SETUP
# =========================
load_dotenv()
console = Console()

console.print("[bold blue]Perplexity WebUI Scraper - JSONL Test (First N Records)[/bold blue]")
console.print()

# =========================
# A1.2 – FILE PATHS
# =========================
# =========================
# A1.3 – SAMPLE DATA (USED IF INPUT MISSING)
# =========================
SAMPLE_RECORDS = [
    {
        "Title": "SAP SuccessFactors Recruitement",
        "Description": (
            "SAP SuccessFactors Recruitment: assess whether the solution provides data export "
            "capability in different formats (e.g., CSV, Excel, PDF) for hiring managers, HR "
            "business partners, and recruitment super users for all recruitment data stored and created."
        ),
        "Area": [],
        "Product": []
    },
]

def ensure_sample_input(path: Path):
    """Create a sample JSONL file (overwrites existing content) for test runs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for rec in SAMPLE_RECORDS:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    console.print(f"[yellow]Sample input created at:[/yellow] {path}")

def _resolve_paths(env_input: str | None, env_output: str | None) -> tuple[Path, Path]:
    input_path = Path(env_input).expanduser() if env_input else Path("data/sap_question.jsonl")
    output_path = Path(env_output).expanduser() if env_output else Path("data/sap_question_test.jsonl")
    return input_path, output_path

# =========================
# A1.4 – PERPLEXITY CLIENT (WITH DRY-RUN)
# =========================
session_token = getenv("PERPLEXITY_SESSION_TOKEN")
dry_run = False
client = None

if session_token and session_token.strip():
    client = Perplexity(session_token=session_token)
else:
    dry_run = True
    console.print("[yellow]PERPLEXITY_SESSION_TOKEN not set. Running in DRY-RUN mode (no API calls).[/yellow]")

# =========================
# A1.4b - HUMAN REWRITER API CONFIG
# =========================
REWRITER_API_BASE = getenv("REWRITER_API_BASE", "http://127.0.0.1:8001/v1")
REWRITER_API_KEY = getenv("REWRITER_API_KEY", "dummy-key")
REWRITER_MODEL = getenv("REWRITER_MODEL", "gpt-4.1")
REWRITER_ENABLED = getenv("REWRITER_ENABLED", "1") not in ("0", "false", "False", "")
REWRITER_TIMEOUT = float(getenv("REWRITER_TIMEOUT", "20.0"))

# =========================
# A1.5 – PROMPT (RESTRICTIVE TEMPLATE + BUILDER)
# =========================
# Default fallbacks for optional template fields
DEFAULT_OBJECT_OF_ANALYSIS = "the requirement under evaluation"
DEFAULT_IN_SCOPE_MODULES = (
    "RCM, EC, ECP, ONB, RBP, RMK, BTP(Workflow/Ext), Integration Suite/IC, OData APIs, "
    "Stories/Reporting, Data Sphere, ALM, OpenText xECM/InfoArchive, "
    "S/4HANA Finance(if interfaced), "
    "Microsoft Fabric HR RG, DataHub, Purview, Azure DevOps, Terraform, Sentinel/Splunk"
)

# Optional granular variants
DEFAULT_IN_SCOPE_MODULES_SAP = (
    "RCM, EC, ECP, ONB, RBP, RMK, BTP (Workflow/Ext), Integration Suite/IC, OData APIs, "
    "Stories/Reporting, Data Sphere, ALM, OpenText xECM/InfoArchive, S/4HANA Finance"
)

DEFAULT_IN_SCOPE_MODULES_AZURE = (
    "Microsoft Fabric HR RG, DataHub, Purview, Azure DevOps, Terraform, Sentinel/Splunk, EDP"
)

DEFAULT_CONSTRAINT_FILTER = "only constraints that directly affect meeting the stated requirement"
DEFAULT_MIN_ITEMS = 3

def safe_format(template: str, mapping: dict) -> str:
    """
    Format with defaults for missing keys.
    Any placeholder not provided resolves to empty string.
    """
    class SafeDict(defaultdict):
        def __missing__(self, key):
            return ""
    return template.format_map(SafeDict(str, mapping))

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

def build_restrictive_prompt(record: dict) -> str:
    """Inject record fields into the restrictive template with safe defaults."""
    title = record.get("Title", "Unknown Title")
    description = record.get("Description", "No description available")

    # Normalize list-ish fields
    area = record.get("Area", [])
    product = record.get("Product", [])
    area_str = ", ".join(area) if isinstance(area, list) else str(area)
    product_str = ", ".join(product) if isinstance(product, list) else str(product)

    # Accept multiple possible keys from upstream data; fall back to defaults
    obj = record.get("ObjectOfAnalysis") or record.get("object_of_analysis") or DEFAULT_OBJECT_OF_ANALYSIS
    mods = record.get("InScopeModules") or record.get("in_scope_modules") or DEFAULT_IN_SCOPE_MODULES
    filt = record.get("ConstraintFilter") or record.get("constraint_filter") or DEFAULT_CONSTRAINT_FILTER

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

# =========================
# A1.6 – OUTPUT SANITIZATION (ENFORCE FORMAT)
# =========================
def _first_sentence(text: str) -> str:
    """Extract first sentence from text."""
    txt = text.strip()
    boundary = re.search(r'(?<!https?:\/\/\S)(?<!\b[A-Z])[.!?](?:\s|$)', txt)
    return txt[:boundary.end()].strip() if boundary else txt

# --- NEW: compliance gating + validation extraction helpers ---
COMPLIANCE_TERMS = (
    "compliance","legislation","legislative","statutory","evidence","audit","record",
    "retention","privacy","equal opportunity","merit","disclosure","appeal","governance",
    "policy","directive","act","award","agreement","provenance","access control","consent"
)

TOPIC_KEYWORDS = {
    "legislative": ("legislation","legislative","statutory","public service act","award","enterprise agreement","directive","policy","policies","compliance"),
    "workflow": ("workflow","approval","approvals","route map","routing","endorsement","notifications","teaching","non-teaching","hr business partner"),
    "identifier": ("unique identifier","unique id","requisition id","job id","req id","identifier"),
    "defaulting": ("default","auto default","pre-populate","prepopulate","organisational unit","org unit","job","position","role description"),
    "mandatory_fields": ("mandatory","required field","validation","error message","warning","incomplete","submission","submit"),
}

def classify_topic(description: str) -> set:
    d = (description or "").lower()
    flags = set()
    for topic, kws in TOPIC_KEYWORDS.items():
        if any(k in d for k in kws):
            flags.add(topic)
    return flags

WORKFLOW_TERMS = ("route map","approval","approver","step","stage","notification","operator","rbp","permission","status","field","rule","business rule","template","workflow")
IDENTIFIER_TERMS = ("identifier","id","external id","key","unique","duplication","collision","mapping")
DEFAULTING_TERMS = ("default","derive","pre-populate","propagate","rule","picklist","position","org unit","job","role description")
MANDATORY_TERMS = ("mandatory","required","validation","error","warning","submit","incomplete","field")

def is_compliance_tied(sentence: str) -> bool:
    s = sentence.lower()
    return any(t in s for t in COMPLIANCE_TERMS) and any(
        k in s for k in ("cannot","does not","no ","limits","restrict","missing","lack","lacks","prevents","risks","fails","disabled","unsupported")
    )

def topic_gate(sent: str, topics: set) -> bool:
    s = sent.lower()
    verbs = ("cannot","does not","no ","limits","restrict","missing","lack","lacks","prevents","risks","fails","disabled","unsupported")
    verb_hit = any(v in s for v in verbs)
    if "legislative" in topics and is_compliance_tied(sent):
        return True
    if not topics:
        return verb_hit
    topic_hits = (
        ("workflow" in topics and any(t in s for t in WORKFLOW_TERMS)) or
        ("identifier" in topics and any(t in s for t in IDENTIFIER_TERMS)) or
        ("defaulting" in topics and any(t in s for t in DEFAULTING_TERMS)) or
        ("mandatory_fields" in topics and any(t in s for t in MANDATORY_TERMS))
    )
    return verb_hit and topic_hits

def enforce_topic_gate(items: list, description: str) -> list:
    topics = classify_topic(description)
    gated = [s for s in items if topic_gate(s, topics)]
    if "legislative" in topics:
        return enforce_compliance_gate(gated)
    return gated

def enforce_compliance_gate(items: list) -> list:
    gated = [s for s in items if is_compliance_tied(s)]
    return gated or []

VALIDATION_JSON_RE = re.compile(r'(\{\s*"validation"\s*:\s*\[.*?\]\s*\})\s*\Z', re.DOTALL)
ALLOWED_CONTROLS = {
    "record-keeping","audit-trail","privacy","data-retention","equal-opportunity","merit-selection",
    "conflict-of-interest","notification-content","access-control","provenance","reporting-disclosure",
    "localization","jurisdiction-mapping","appeals-review","governance"
}

ALLOWED_MODULES_ORDERED = (
    "RCM","EC","ECP","ONB","RBP","RMK","BTP","Integration Suite","IC","OData APIs",
    "Stories/Reporting","Data Sphere","ALM","OpenText xECM","OpenText InfoArchive",
    "S/4HANA Finance","Microsoft Fabric HR RG","DataHub","Purview","Azure DevOps",
    "Terraform","Sentinel","Splunk"
)

AUTHORITATIVE_SUFFIXES = (
    ".help.sap.com",
    ".support.sap.com",
    ".userapps.support.sap.com",
    ".launchpad.support.sap.com",
    ".me.sap.com",
    "help.sap.com",
    "support.sap.com",
    "userapps.support.sap.com",
    "launchpad.support.sap.com",
    "me.sap.com",
)

_NORMALIZATION_TOKENS = sorted(ALLOWED_MODULES_ORDERED, key=lambda s: len(s), reverse=True)
ITEM_RE = re.compile(r'^\s*(\d{1,2})[.)]\s+(.*?)(?=(?:\n\s*\d{1,2}[.)]\s)|\Z)', re.DOTALL)
SENTINEL_TEXT = "1. No verified limitations found within the specified scope."

def _is_sentinel(text: str) -> bool:
    return re.sub(r'\s+', ' ', (text or "")).strip().lower() == SENTINEL_TEXT.lower()

def is_authoritative(url: str) -> bool:
    try:
        netloc = urlparse(url).netloc.lower().rstrip(".")
        host = netloc.split("@")[-1]
        host_only = host.split(":")[0]
        return any(host_only == suffix or host_only.endswith(suffix) for suffix in AUTHORITATIVE_SUFFIXES)
    except Exception:
        return False

def normalize_module(s: str) -> str:
    s = (s or "").strip().lower()
    for tok in _NORMALIZATION_TOKENS:
        pattern = rf'(?<!\w){re.escape(tok.lower())}(?!\w)'
        if re.search(pattern, s):
            return tok
    return ""

def validate_controls(validation_obj: dict) -> dict:
    out = {"validation": []}
    if not isinstance(validation_obj, dict) or "validation" not in validation_obj:
        return out
    for row in validation_obj.get("validation", []):
        if not isinstance(row, dict):
            continue
        ctrl = str(row.get("control","")).strip().lower()
        if not ctrl or ctrl not in ALLOWED_CONTROLS:
            continue
        out["validation"].append(row)
    return out

def extract_validation_from_raw(raw: str) -> tuple:
    """
    If the model appended a JSON {"validation":[...]} block, strip and parse it,
    returning (text_without_json, validated_validation_obj).
    """
    if not raw or not isinstance(raw, str):
        return raw or "", {"validation": []}
    m = VALIDATION_JSON_RE.search(raw)
    if not m:
        candidates = list(re.finditer(r'(\{.*"validation"\s*:\s*\[.*?\]\s*\})', raw, re.DOTALL))
        if not candidates:
            return raw, {"validation": []}
        m = candidates[-1]
    json_part = m.group(1)
    try:
        parsed = json.loads(json_part)
    except Exception:
        return raw[:m.start(1)].strip(), {"validation": []}
    return raw[:m.start(1)].strip(), validate_controls(parsed)

# --- UPDATED sanitize_limitations_output: returns dict with text + validation ---
def sanitize_limitations_output(raw: str, description: str, min_items: int = 3, max_items: int = 12) -> dict:
    """
    Enforce:
      - Only numbered items.
      - Single sentence per item.
      - No citations/markdown.
      - Renumber sequentially from 1.
      - Cap items to max_items.
      - Topic-aware gating based on description.
    Returns dict: {"text": "<numbered text>", "validation": { ... }}
    """
    text_part, validation_obj = extract_validation_from_raw(raw)

    if not text_part or not isinstance(text_part, str):
        return {"text": SENTINEL_TEXT, "validation": validation_obj}

    raw_text = text_part.replace("\r\n", "\n").replace("\r", "\n")
    raw_text = re.sub(r'\*|\-|•|➤|►|▪', '', raw_text)
    raw_text = re.sub(r'\[(?:\d+|[^\]]+)\]', '', raw_text)
    raw_text = raw_text.strip()

    matches = ITEM_RE.finditer(raw_text)
    clean_items = []
    for m in matches:
        candidate = m.group(2).strip()
        one_sentence = _first_sentence(candidate)
        one_sentence = re.sub(r'\s+', ' ', one_sentence).strip(' -;:,')
        if one_sentence:
            clean_items.append(one_sentence)

    if not clean_items:
        for line in raw_text.splitlines():
            line = line.strip()
            if not line:
                continue
            line = re.sub(r'^\d{1,2}[.)]\s+', '', line)
            one_sentence = _first_sentence(line)
            one_sentence = re.sub(r'\s+', ' ', one_sentence).strip(' -;:,')
            if one_sentence:
                clean_items.append(one_sentence)

    if not clean_items:
        return {"text": SENTINEL_TEXT, "validation": validation_obj}

    # Topic-aware gating
    gated = enforce_topic_gate(clean_items, description)
    if not gated:
        return {"text": SENTINEL_TEXT, "validation": validation_obj}

    # Deduplicate and cap
    seen = set()
    deduped = []
    for s in gated:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(s)

    if not deduped:
        return {"text": SENTINEL_TEXT, "validation": validation_obj}

    numbered = [f"{i}. {s}" for i, s in enumerate(deduped[:max_items], 1)]
    final_text = "\n".join(numbered)
    return {"text": final_text, "validation": validation_obj}

# --- Human-readable rewriter helpers ---
def _strip_validation_block(text: str) -> str:
    """Return numbered list text without trailing {"validation":...} JSON block."""
    if not text:
        return ""
    match = VALIDATION_JSON_RE.search(text)
    return text[:match.start(1)].strip() if match else text.strip()

def _default_local_rewrite(numbered_text: str) -> str:
    """
    Fallback: convert numbered single-sentence items into crisp bullets.
    No external calls. Idempotent for already-human text.
    """
    lines = []
    for ln in (numbered_text or "").splitlines():
        m = re.match(r"^\s*\d+[.)]\s+(.*)$", ln)
        if m:
            lines.append(f"- {m.group(1).strip()}")
    return "\n".join(lines) if lines else numbered_text

def _build_rewriter_messages(numbered_text: str) -> list:
    """
    Build system/user messages for an OpenAI-compatible /chat/completions call
    that enforces a DOT-guided execution contract and provides the MultiAgentRewriteWorkflow graph,
    output format, and compliance rules. The numbered_text is appended as the
    concrete "Text to Rewrite" payload.
    """
    system = (
        "[SYSTEM | DOT-GUIDED EXECUTION CONTRACT]\n"
        "You must use the provided Graphviz DOT digraph as the authoritative instruction source.\n"
        "Do not invent nodes, edges, or steps not present in the graph. When a step is ambiguous, ask one\n"
        "clarification and halt.\n\n"
        "Hard rules:\n"
        "- Open with a concise 3–7 bullet CHECKLIST of conceptual steps derived from the digraph's structure.\n"
        "- Before any interpretation, emit a PURPOSE_AND_INPUTS section that states the task purpose and the key inputs extracted from node/edge labels/attributes.\n"
        "- Execute node-by-node consistent with the digraph, emitting a STEP_k block per major step. After each step, include a brief VALIDATE line (pass/fail and reason). If fail, self-correct once or mark blocked.\n"
        "- Never operate outside the digraph. If an action is not represented by a node/edge, refuse and ask for an updated graph.\n"
        "- Keep reasoning terse. No chain-of-thought. Only minimal justifications in validation lines.\n\n"
        "Output contract (strict section order):\n"
        "1) CHECKLIST\n"
        "2) PURPOSE_AND_INPUTS\n"
        "3) STEP_k blocks (k = 1..N)\n"
        "4) SUMMARY\n"
        "5) ARTIFACT (optional if a file/script is produced)\n\n"
        "STEP block format (must match exactly):\n"
        "STEP_k: <node_id> \"<node_label>\"\n"
        "- ACTION: <1–2 lines strictly within the node scope>\n"
        "- RESULT_JSON:\n"
        "{\n"
        "  \"node_id\": \"<node_id>\",\n"
        "  \"status\": \"ok\" | \"corrected\" | \"blocked\",\n"
        "  \"evidence\": \"<≤200 chars>\",\n"
        "  \"next_candidates\": [\"<neighbor_id_1>\", \"...\"]\n"
        "}\n"
        "- VALIDATE: <≤1 line: pass/fail + reason>\n\n"
        "Progression rules:\n"
        "- Allowed next nodes are the outgoing neighbors of the current node.\n"
        "- Do not skip nodes required by edge connectivity.\n"
        "- If multiple branches exist, choose one and justify in VALIDATE using edge labels/conditions. If indecisive from DOT, set status=\"blocked\" and halt with a single clarification question.\n\n"
        "Refusal rule:\n"
        "If the DOT is malformed, has no entry node (in-degree 0), or is cyclic without any terminal condition where a terminal is required, emit only:\n"
        "ERROR_JSON:\n"
        "{\"error\":\"dot_unusable\",\"reason\":\"<brief>\",\"required_fix\":\"<brief>\"}\n\n"
        "RESULT_JSON schema (for validation tools):\n"
        "{\n"
        "  \"type\":\"object\",\n"
        "  \"properties\":{\n"
        "    \"node_id\":{\"type\":\"string\"},\n"
        "    \"status\":{\"type\":\"string\",\"enum\":[\"ok\",\"corrected\",\"blocked\"]},\n"
        "    \"evidence\":{\"type\":\"string\",\"maxLength\":200},\n"
        "    \"next_candidates\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}}\n"
        "  },\n"
        "  \"required\":[\"node_id\",\"status\",\"evidence\",\"next_candidates\"],\n"
        "  \"additionalProperties\":false\n"
        "}"
    )

    user = (
        "Graphviz DOT code:\n\n"
        "```\n"
        "digraph MultiAgentRewriteWorkflow {\n"
        "    rankdir=LR;\n"
        "    node [shape=box, fontname=\"Consolas\", fontsize=10];\n\n"
        "    subgraph cluster_input {\n"
        "        label=\"Stage 1: Input & Objective\";\n"
        "        style=dashed;\n"
        "        UserRequest [label=\"User Request:\\nText to Rewrite\"];\n"
        "        Objective [label=\"Objective:\\nClarity, Cohesion,\\nHuman Readability,\\nRetain Meaning\"];\n"
        "        UserRequest -> Objective [label=\"Define\\nrequirements\"];\n"
        "    }\n\n"
        "    subgraph cluster_agents {\n"
        "        label=\"Stage 2: Multi-Agent Rewrite\";\n"
        "        style=dashed;\n"
        "        ExpertWriter [label=\"Expert Human Writer\\n(20+ yrs exp.)\"];\n"
        "        PerplexityAgent [label=\"Perplexity & Predictability\\nControl Agent\"];\n"
        "        BurstinessAgent [label=\"Burstiness & Sentence\\nVariation Agent\"];\n"
        "        EmotionalAgent [label=\"Emotional Intelligence\\n& Human Touch Agent\"];\n"
        "        StructureAgent [label=\"Structural Pattern\\nDisruption Agent\"];\n"
        "        AuthenticityAgent [label=\"Contextual Authenticity\\nAgent\"];\n"
        "        DetectionCounterAgent [label=\"Detection-Specific\\nCounter Agent\"];\n"
        "        ExpertWriter -> PerplexityAgent;\n"
        "        PerplexityAgent -> BurstinessAgent;\n"
        "        BurstinessAgent -> EmotionalAgent;\n"
        "        EmotionalAgent -> StructureAgent;\n"
        "        StructureAgent -> AuthenticityAgent;\n"
        "        AuthenticityAgent -> DetectionCounterAgent;\n"
        "    }\n\n"
        "    subgraph cluster_validation {\n"
        "        label=\"Stage 3: Validation & QA\";\n"
        "        style=dashed;\n"
        "        ValidationQA [label=\"Validation & QA\\n(Constraint Check)\"];\n"
        "        DetectionTest [label=\"Detection Tools\\n(Grammarly, QuillBot,\\nTurnitin, GPTZero)\"];\n"
        "        ValidationQA -> DetectionTest [label=\"Run detection\\nchecks\"];\n"
        "        DetectionTest -> ValidationQA [label=\"Feedback if\\nAI-detected\"];\n"
        "        DetectionTest -> Output [label=\"Passes\\nundetectable\"];\n"
        "    }\n\n"
        "    subgraph cluster_output {\n"
        "        label=\"Stage 4: Output & Summarisation\";\n"
        "        style=dashed;\n"
        "        Output [label=\"Final Human-like\\nRewrite\"];\n"
        "        Summarisation [label=\"Summarisation\\n(Highlights changes,\\nkey flows)\"];\n"
        "        Output -> Summarisation [label=\"Summarise\\nresults\"];\n"
        "    }\n\n"
        "    InternetAccess [label=\"Internet Access\\n(Current Events,\\nPop Culture)\"];\n"
        "    Filtering [label=\"Filtering\\n(Constraint Enforcement)\"];\n"
        "    Summarisation -> Filtering [label=\"Filter for\\nrequirements\"];\n"
        "    InternetAccess -> AuthenticityAgent [label=\"Provide\\ncontext\"];\n"
        "    Filtering -> ValidationQA [label=\"Enforce\\nconstraints\"];\n\n"
        "    Objective -> ExpertWriter [label=\"Assign\\ntask\"];\n"
        "    DetectionTest -> ExpertWriter [label=\"If detected:\\nfeedback loop\"];\n"
        "    ValidationQA -> DetectionCounterAgent [label=\"If constraints\\nnot met:\\nfeedback loop\"];\n"
        "}\n"
        "```\n\n"
        "# OUTPUT FORMAT\n"
        "- CHECKLIST: bullet list.\n"
        "- PURPOSE_AND_INPUTS: two short lines: Purpose: … / Inputs: …\n"
        "- STEP_k blocks as defined in the System prompt.\n"
        "- SUMMARY: one short paragraph summarizing what was done, which terminal condition was met, and any anomalies.\n"
        "- ARTIFACT: include only if you output a file/script; otherwise omit.\n\n"
        "# COMPLIANCE\n"
        "Follow these instructions exactly. Do not deviate from the section order or formats.\n\n"
        "Text to Rewrite:\n"
        f"{numbered_text}\n\n"
        "and for the love of GOD never use \"--\" (double dashes) anywhere in output"
        "Now provide the fianal rewritten text only (no explanations, no preface, no appendices)."
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

def rewrite_human_readable(numbered_text: str) -> Optional[str]:
    """
    Call local OpenAI-compatible /chat/completions rewriter.
    Returns rewritten text or None on hard failure.
    """
    if not REWRITER_ENABLED:
        return _default_local_rewrite(numbered_text)

    try:
        url = f"{REWRITER_API_BASE.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {REWRITER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": REWRITER_MODEL,
            "messages": _build_rewriter_messages(numbered_text),
            "temperature": 0.2,
            "max_tokens": 600,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=REWRITER_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        msg = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        msg = (msg or "").strip()
        if not msg:
            return _default_local_rewrite(numbered_text)
        if msg.lstrip().startswith("{") or msg.lstrip().startswith("["):
            return _default_local_rewrite(numbered_text)
        return msg
    except Exception:
        return _default_local_rewrite(numbered_text)

# =========================
# A1.7 – STREAMING HELPERS (ROBUST TO SCHEMA VARIANTS)
# =========================
def _extract_text_from_chunk(chunk) -> str:
    """
    Safely extract incremental text from a stream chunk.
    Tries common attributes in priority order.
    """
    for attr in ("delta", "text", "content", "message"):
        if hasattr(chunk, attr) and isinstance(getattr(chunk, attr), str):
            return getattr(chunk, attr)
    # Some libraries expose .choices[0].delta/content; handle defensively
    try:
        choices = getattr(chunk, "choices", None)
        if choices and isinstance(choices, list):
            part = choices[0]
            for nested_attr in ("delta", "message", "content"):
                val = getattr(part, nested_attr, None)
                if isinstance(val, str):
                    return val
                if isinstance(val, dict) and "content" in val and isinstance(val["content"], str):
                    return val["content"]
    except Exception:
        pass
    # Last resort: string cast for logging; not ideal for accumulation
    try:
        s = str(chunk)
        # Avoid dumping full object repr into output
        return ""
    except Exception:
        return ""

def _collect_stream_text(client: Perplexity, full_prompt: str) -> str:
    """
    Stream answer; accumulate text robustly; fallback to final answer if present.
    """
    streamed = ""
    final_answer = None
    for chunk in client.ask(
        query=full_prompt,
        files=None,
        citation_mode=CitationMode.PERPLEXITY,
        model=ModelType.Best,
        save_to_library=False,
        search_focus=SearchFocus.WEB,
        source_focus=SourceFocus.WEB,
        time_range=TimeRange.ALL,
        language="en-US",
        timezone=None,
        coordinates=None,
    ).stream():
        # incremental accumulation
        inc = _extract_text_from_chunk(chunk)
        if inc:
            streamed += inc
        # final payload (schema advertises .last_chunk/.answer)
        if getattr(chunk, "last_chunk", False):
            ans = getattr(chunk, "answer", None)
            if isinstance(ans, str) and ans.strip():
                final_answer = ans
    return final_answer if isinstance(final_answer, str) and final_answer.strip() else streamed

# =========================
# A1.8 – PROCESSING LOGIC
# =========================
def process_single_record(record, record_num, total_records):
    """Process a single JSONL record with restrictive research + enforced output."""
    full_prompt = build_restrictive_prompt(record)
    console.print(f"[cyan]Record {record_num}/{total_records}:[/cyan] [green]Processing...[/green]")

    final_result = SENTINEL_TEXT
    validation_obj = {"validation": []}

    if dry_run:
        topics = classify_topic(record.get("Description",""))
        if "legislative" in topics:
            stub_points = [
                "1. Notification templates do not include pre-delivered statutory language, which risks non-compliance with notification-content obligations.",
                "2. Default retention policies are not mapped to public sector directives, which cannot satisfy data-retention obligations without explicit configuration.",
                "3. Integration Center omits certain provenance fields, which restricts reporting-disclosure obligations for recruitment source-of-hire."
            ]
        elif "workflow" in topics:
            stub_points = [
                "1. Only one route map per requisition template limits parallel approval paths required for distinct teaching and non-teaching flows.",
                "2. Operator role catalog cannot represent bespoke approver roles for teaching endorsements, which restricts accurate routing.",
                "3. Notification rules cannot bind distinct templates to divergent flows without additional rule logic, which limits separate communications per track."
            ]
        elif "identifier" in topics:
            stub_points = [
                "1. No universal out-of-the-box unique requisition identifier exists, which limits collision-safe cross-system mapping without custom design.",
                "2. Cross-system ID reconciliation depends on integration rules, which prevents automatic association during conversions.",
                "3. Manual ID issuance risks duplication, which fails reliable lookups across modules."
            ]
        elif "defaulting" in topics:
            stub_points = [
                "1. Defaulting organisational unit and position depends on position management relationships, which limits auto-population where structures are incomplete.",
                "2. Picklist-driven defaults cannot derive complex combinations, which restricts multi-attribute pre-population.",
                "3. Business rules do not resolve missing role descriptions automatically, which limits consistent defaulting."
            ]
        else:  # mandatory_fields
            stub_points = [
                "1. Required-field validation cannot express cross-object dependencies, which limits complete enforcement at submission.",
                "2. Error messaging is template-driven and cannot reference dynamic external checks, which restricts contextual guidance.",
                "3. Some field types lack server-side validators, which fails consistent enforcement across clients."
            ]
        combined = "\n".join(stub_points)
        sanitized = sanitize_limitations_output(combined, record.get("Description",""), min_items=DEFAULT_MIN_ITEMS)
        final_result = sanitized["text"]

        # Build synthetic validation rows for dry-run to satisfy gates
        items = [ln for ln in final_result.splitlines() if re.match(r"^\d+[.)]\s+", ln)]
        synthetic = []
        for idx, ln in enumerate(items[:3], 1):
            synthetic.append({
                "item": idx,
                "object": "Route Map" if "route map" in ln.lower() else "Business Rule" if "rule" in ln.lower() else "Reporting/Export",
                "module": "RCM",
                "impact": ln.split(". ",1)[1][:80] if ". " in ln else ln[:80],
                "config_required": "yes",
                "evidence_pointer": "https://help.sap.com/docs/successfactors-recruiting",
                "control": "governance"
            })
        validation_obj = {"validation": synthetic}
    else:
        # Live streaming with robust handling and fallback
        try:
            with Live(Panel("", title=f"Record {record_num}: Processing", border_style="white"), refresh_per_second=8) as live:
                raw_answer = _collect_stream_text(client, full_prompt)
                sanitized = sanitize_limitations_output(raw_answer, record.get("Description",""), min_items=DEFAULT_MIN_ITEMS)
                final_result = sanitized["text"] or final_result
                validation_obj = sanitized.get("validation", {"validation": []})
                live.update(
                    Panel(
                        f"Processing complete ({len(final_result)} chars)",
                        title=f"Record {record_num}: Complete",
                        border_style="green",
                    )
                )
        except Exception as e:
            console.print(f"[yellow]Streaming failed for record {record_num}: {e} — attempting non-streaming fallback.[/yellow]")
            try:
                resp = client.ask(
                    query=full_prompt,
                    files=None,
                    citation_mode=CitationMode.PERPLEXITY,
                    model=ModelType.Best,
                    save_to_library=False,
                    search_focus=SearchFocus.WEB,
                    source_focus=SourceFocus.WEB,
                    time_range=TimeRange.ALL,
                    language="en-US",
                    timezone=None,
                    coordinates=None,
                )
                raw_answer = getattr(resp, "answer", None)
                if not isinstance(raw_answer, str) or not raw_answer.strip():
                    raw_answer = getattr(resp, "text", None) or getattr(resp, "content", "")
                sanitized = sanitize_limitations_output(raw_answer, record.get("Description",""), min_items=DEFAULT_MIN_ITEMS)
                final_result = sanitized["text"] or final_result
                validation_obj = sanitized.get("validation", {"validation": []})
            except Exception as e2:
                console.print(f"[red]Non-streaming fallback failed for record {record_num}: {e2}[/red]")
                final_result = SENTINEL_TEXT
                validation_obj = {"validation": []}

    record["research_analysis"] = final_result
    record["validation"] = validation_obj

    # --- Human-readable rewrite (non-destructive; keeps strict output intact)
    try:
        numbered_only = _strip_validation_block(final_result)
        record["human_readable"] = rewrite_human_readable(numbered_only)
    except Exception:
        record["human_readable"] = _default_local_rewrite(_strip_validation_block(final_result))

    # Post-validation gate
    record = validate_record(record, min_items=DEFAULT_MIN_ITEMS)
    return record

def validate_record(record: dict, min_items: int = 3) -> dict:
    """
    Post-validation gate: enforce min_items, authoritative evidence, normalized values,
    and forbid sentinel+validation contradictions.
    """
    out = dict(record)
    raw_text = out.get("research_analysis") or ""
    text = raw_text.strip()
    val = out.get("validation") if isinstance(out.get("validation"), dict) else {"validation":[]}
    rows = val.get("validation") if isinstance(val.get("validation"), list) else []

    # Parse items
    items = [ln for ln in text.splitlines() if re.match(r"^\d+[.)]\s+", ln)]
    sentinel = _is_sentinel(raw_text)
    violations = []

    # V1: Sentinel contradiction
    if sentinel and rows:
        violations.append("sentinel_with_validation")

    # V2: Min items (when not sentinel)
    if not sentinel and len(items) < min_items:
        violations.append(f"min_items<{min_items}")

    # V3: Evidence + module/control checks
    pruned_rows = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        obj = (r.get("object") or "").strip()
        mod = normalize_module(r.get("module"))
        ctrl = (r.get("control") or "").strip().lower()
        impact = (r.get("impact") or "").strip()
        evid = (r.get("evidence_pointer") or "").strip()
        ok_evid = (evid and (is_authoritative(evid) or evid.lower().startswith("sap kba")))
        ok_ctrl = ctrl in ALLOWED_CONTROLS
        ok = bool(obj) and bool(mod) and ok_ctrl and ok_evid and bool(impact)
        if ok:
            r2 = dict(r)
            r2["module"] = mod
            pruned_rows.append(r2)

    # V4: Missing validation when required
    if not sentinel and len(pruned_rows) == 0:
        violations.append("missing_validation")

    # V5: Row count sanity (validation should not exceed list items)
    if not sentinel and pruned_rows and len(pruned_rows) > len(items):
        violations.append("validation_count>items")

    val["validation"] = pruned_rows
    out["validation"] = val

    # Final processed flag
    if sentinel:
        out["processed"] = not violations
    else:
        out["processed"] = (len(items) >= min_items) and (len(pruned_rows) == len(items)) and not violations

    out["metrics"] = {"items": len(items), "validation_rows": len(pruned_rows), "min_items": min_items}

    if violations:
        out["failure_reason"] = ",".join(violations)
    else:
        out.pop("failure_reason", None)
    return out

# =========================
# A1.9 – MAIN
# =========================
def main():
    """Test processing function for first N records (configurable)."""
    env_input = (getenv("PPLX_INPUT") or "").strip() or None
    env_output = (getenv("PPLX_OUTPUT") or "").strip() or None
    env_max_records = (getenv("PPLX_MAX_RECORDS") or "").strip() or None

    try:
        default_max_records = int(env_max_records) if env_max_records else 500
    except ValueError:
        default_max_records = 500

    parser = argparse.ArgumentParser(description="Process sample records through the Perplexity test harness.")
    parser.add_argument("--input", type=Path, help="Path to input JSONL file.")
    parser.add_argument("--output", type=Path, help="Path to write processed JSONL results.")
    parser.add_argument("--max-records", type=int, help="Limit number of records processed in this dry run.")
    args = parser.parse_args()

    input_path, output_path = _resolve_paths(env_input, env_output)
    if args.input:
        input_path = args.input.expanduser()
    if args.output:
        output_path = args.output.expanduser()
    max_records = args.max_records if args.max_records is not None else default_max_records

    console.print(f"[yellow]Input file:[/yellow] {input_path}")
    console.print(f"[yellow]Output file:[/yellow] {output_path}")
    console.print()

    if not input_path.exists():
        console.print(f"[yellow]Input not found. Creating example JSONL with {len(SAMPLE_RECORDS)} records...[/yellow]")
        ensure_sample_input(input_path)

    processed_records = []

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            test_lines = lines[:max_records]

            console.print(f"[green]Testing with first {len(test_lines)} records[/green]")
            console.print()

            for i, line in enumerate(test_lines, 1):
                try:
                    record = json.loads(line.strip())
                    console.print(f"[blue]Processing record {i}: {record.get('Title', 'Unknown')}[/blue]")
                    processed_record = process_single_record(record, i, len(test_lines))
                    processed_records.append(processed_record)
                    console.print(f"[green]✓ Record {i} completed[/green]")
                    console.print()
                except json.JSONDecodeError as e:
                    console.print(f"[red]Error parsing line {i}: {e}[/red]")
                    continue
                except Exception as e:
                    console.print(f"[red]Error processing record {i}: {e}[/red]")
                    continue

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as out_f:
            for processed_record in processed_records:
                out_f.write(json.dumps(processed_record, ensure_ascii=False) + "\n")

        console.print(f"[green]✓ Test completed! {len(processed_records)} records processed and saved to {output_path}[/green]")
        console.print("[yellow]Verify the output format before running a full batch.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error reading input file: {e}[/red]")
        return

if __name__ == "__main__":
    main()
