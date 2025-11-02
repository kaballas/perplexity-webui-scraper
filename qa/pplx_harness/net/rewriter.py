"""Optional human-readable rewrite helpers."""

from __future__ import annotations

import re
from os import getenv
from typing import Any

import requests

from ..text.regexes import VALIDATION_JSON_RE

__all__ = ["rewrite_human_readable", "strip_validation_block"]


REWRITER_API_BASE = getenv("REWRITER_API_BASE", "http://127.0.0.1:8001/v1")
REWRITER_API_KEY = getenv("REWRITER_API_KEY", "dummy-key")
REWRITER_MODEL = getenv("REWRITER_MODEL", "gpt-4.1")
REWRITER_ENABLED = getenv("REWRITER_ENABLED", "1") not in ("0", "false", "False", "")
REWRITER_TIMEOUT = float(getenv("REWRITER_TIMEOUT", "20.0"))


def strip_validation_block(text: str) -> str:
    """Return numbered text without a trailing validation JSON block."""
    if not text:
        return ""
    match = VALIDATION_JSON_RE.search(text)
    return text[: match.start(1)].strip() if match else text.strip()


def _default_local_rewrite(numbered_text: str) -> str:
    lines: list[str] = []
    for line in (numbered_text or "").splitlines():
        match = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if match:
            lines.append(f"- {match.group(1).strip()}")
    return "\n".join(lines) if lines else numbered_text


def _build_rewriter_messages(numbered_text: str) -> list[dict[str, Any]]:
    """Compose chat messages enforcing the DOT-guided execution contract."""
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
        '  "node_id": "<node_id>",\n'
        '  "status": "ok" | "corrected" | "blocked",\n'
        '  "evidence": "<≤200 chars>",\n'
        '  "next_candidates": ["<neighbor_id_1>", "..."]\n'
        "}\n"
        "- VALIDATE: <≤1 line: pass/fail + reason>\n\n"
        "Progression rules:\n"
        "- Allowed next nodes are the outgoing neighbors of the current node.\n"
        "- Do not skip nodes required by edge connectivity.\n"
        "- If multiple branches exist, choose one and justify in VALIDATE using edge labels/conditions. If indecisive from DOT, set status=\"blocked\" and halt with a single clarification question.\n\n"
        "Refusal rule:\n"
        "If the DOT is malformed, has no entry node (in-degree 0), or is cyclic without any terminal condition where a terminal is required, emit only:\n"
        'ERROR_JSON:\n{"error":"dot_unusable","reason":"<brief>","required_fix":"<brief>"}\n\n'
        "RESULT_JSON schema (for validation tools):\n"
        "{\n"
        '  "type":"object",\n'
        '  "properties":{\n'
        '    "node_id":{"type":"string"},\n'
        '    "status":{"type":"string","enum":["ok","corrected","blocked"]},\n'
        '    "evidence":{"type":"string","maxLength":200},\n'
        '    "next_candidates":{"type":"array","items":{"type":"string"}}\n'
        "  },\n"
        '  "required":["node_id","status","evidence","next_candidates"],\n'
        '  "additionalProperties":false\n'
        "}"
    )

    user = (
        "Graphviz DOT code:\n\n"
        "```\n"
        "digraph MultiAgentRewriteWorkflow {\n"
        '    rankdir=LR;\n    node [shape=box, fontname="Consolas", fontsize=10];\n\n'
        "    subgraph cluster_input {\n"
        '        label="Stage 1: Input & Objective";\n        style=dashed;\n'
        '        UserRequest [label="User Request:\\nText to Rewrite"];\n'
        '        Objective [label="Objective:\\nClarity, Cohesion,\\nHuman Readability,\\nRetain Meaning"];\n'
        '        UserRequest -> Objective [label="Define\\nrequirements"];\n'
        "    }\n\n"
        "    subgraph cluster_agents {\n"
        '        label="Stage 2: Multi-Agent Rewrite";\n        style=dashed;\n'
        '        ExpertWriter [label="Expert Human Writer\\n(20+ yrs exp.)"];\n'
        '        PerplexityAgent [label="Perplexity & Predictability\\nControl Agent"];\n'
        '        BurstinessAgent [label="Burstiness & Sentence\\nVariation Agent"];\n'
        '        EmotionalAgent [label="Emotional Intelligence\\n& Human Touch Agent"];\n'
        '        StructureAgent [label="Structural Pattern\\nDisruption Agent"];\n'
        '        AuthenticityAgent [label="Contextual Authenticity\\nAgent"];\n'
        '        DetectionCounterAgent [label="Detection-Specific\\nCounter Agent"];\n'
        "        ExpertWriter -> PerplexityAgent;\n"
        "        PerplexityAgent -> BurstinessAgent;\n"
        "        BurstinessAgent -> EmotionalAgent;\n"
        "        EmotionalAgent -> StructureAgent;\n"
        "        StructureAgent -> AuthenticityAgent;\n"
        "        AuthenticityAgent -> DetectionCounterAgent;\n"
        "    }\n\n"
        "    subgraph cluster_validation {\n"
        '        label="Stage 3: Validation & QA";\n        style=dashed;\n'
        '        ValidationQA [label="Validation & QA\\n(Constraint Check)"];\n'
        '        DetectionTest [label="Detection Tools\\n(Grammarly, QuillBot,\\nTurnitin, GPTZero)"];\n'
        "        ValidationQA -> DetectionTest [label=\"Run detection\\nchecks\"];\n"
        "        DetectionTest -> ValidationQA [label=\"Feedback if\\nAI-detected\"];\n"
        "        DetectionTest -> Output [label=\"Passes\\nundetectable\"];\n"
        "    }\n\n"
        "    subgraph cluster_output {\n"
        '        label="Stage 4: Output & Summarisation";\n        style=dashed;\n'
        '        Output [label="Final Human-like\\nRewrite"];\n'
        '        Summarisation [label="Summarisation\\n(Highlights changes,\\nkey flows)"];\n'
        "        Output -> Summarisation [label=\"Summarise\\nresults\"];\n"
        "    }\n\n"
        '    InternetAccess [label="Internet Access\\n(Current Events,\\nPop Culture)"];\n'
        '    Filtering [label="Filtering\\n(Constraint Enforcement)"];\n'
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
        'and for the love of GOD never use "--" (double dashes) anywhere in output'
        "Now provide the fianal rewritten text only (no explanations, no preface, no appendices)."
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def rewrite_human_readable(numbered_text: str) -> str:
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
        response = requests.post(url, headers=headers, json=payload, timeout=REWRITER_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        message = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        message = (message or "").strip()
        if not message:
            return _default_local_rewrite(numbered_text)
        if message.lstrip().startswith("{") or message.lstrip().startswith("["):
            return _default_local_rewrite(numbered_text)
        return message
    except Exception:
        return _default_local_rewrite(numbered_text)
