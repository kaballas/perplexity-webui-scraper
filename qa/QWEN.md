### Usage Instructions (Follow Exactly)
First {digraph RepoRecon {
  rankdir=LR;
  node [shape=box, style=rounded];

  // Decisions
  DecisionActivity   [shape=diamond, label="Enough recent activity?"];
  DecisionHotspots   [shape=diamond, label="Hotspots or odd patterns?"];
  DecisionBranches   [shape=diamond, label="Merges/branches need review?"];
  DecisionDeeper     [shape=diamond, label="Need deeper context now?"];

  start [shape=circle, label="Start"];
  end   [shape=doublecircle, label="Done"];

  // 1. Confirm repo and remotes
  subgraph cluster_1 {
    label = "1) Confirm repo & remotes";
    color = lightgrey;
    s1a [label="git status"];
    s1b [label="git remote -v"];
    s1c [label="git branch -vv"];
    s1a -> s1b -> s1c;
  }

  // 2. Inspect latest commits (overview)
  subgraph cluster_2 {
    label = "2) Latest commits (overview)";
    color = lightgrey;
    s2a [label="git log --oneline --graph --decorate -n 20"];
    s2b [label="git show -1 --stat"];
    s2c [label="git show -1 --name-only --pretty="];
    s2a -> s2b -> s2c;
  }

  // 3. Project history & hotspots
  subgraph cluster_3 {
    label = "3) History & hotspots";
    color = lightgrey;
    s3a [label="git shortlog -sn"];
    s3b [label="git log --stat | less"];
    s3c [label="git log --since='3 months ago' --oneline | wc -l"];
    s3d [label="git blame README.md | head -n 10"];
    s3a -> s3b -> s3c -> s3d;
  }

  // 4. Understand structure
  subgraph cluster_4 {
    label = "4) Understand structure";
    color = lightgrey;
    s4a [label="git ls-tree -r HEAD --name-only | head -n 50"];
    s4b [label="git ls-tree -d -r HEAD | grep -E '(src|app|tests|docs|config)'"];
    s4a -> s4b;
  }

  // 5. Identify tech stack (indirect)
  subgraph cluster_5 {
    label = "5) Identify tech stack";
    color = lightgrey;
    s5a [label="git grep -i 'import' | head -n 20"];
    s5b [label="git grep -i 'def ' | head -n 20"];
    s5c [label="git grep -i 'class ' | head -n 20"];
    s5d [label="git ls-files | grep -E '(package.json|pyproject.toml|go.mod|Cargo.toml|Makefile|Dockerfile)'"];
    s5a -> s5b -> s5c -> s5d;
  }

  // 6. Branches, merges, tags
  subgraph cluster_6 {
    label = "6) Branches, merges, tags";
    color = lightgrey;
    s6a [label="git log --merges --oneline -n 10"];
    s6b [label="git branch -r"];
    s6c [label="git tag --sort=-creatordate | head -n 10"];
    s6a -> s6b -> s6c;
  }

  // 7. Optional deeper context
  subgraph cluster_7 {
    label = "7) Optional deeper context";
    color = lightgrey;
    s7a [label="git log -p -n 3"];
    s7b [label="git diff HEAD~1 HEAD --stat"];
    s7c [label="git show HEAD~1"];
    s7a -> s7b -> s7c;
  }

  // Global flow
  start -> s1a;
  s1c -> s2a -> s3a -> DecisionActivity;
  DecisionActivity -> s4a [label="yes"];
  DecisionActivity -> s2a [label="no, re-check timeline"];

  s4b -> s5a -> DecisionHotspots;
  DecisionHotspots -> s7a [label="yes"];
  DecisionHotspots -> s6a [label="no"];

  s6c -> DecisionBranches;
  DecisionBranches -> s7a [label="yes"];
  DecisionBranches -> DecisionDeeper [label="no"];

  // Optional deeper dive loop
  s7c -> DecisionDeeper;
  DecisionDeeper -> s2a [label="loop for more"];
  DecisionDeeper -> end   [label="good enough"];
}
}
Second {
[ChatMessage(role='system', content='[SYSTEM | DOT-GUIDED EXECUTION CONTRACT]\nYou must use the provided Graphviz DOT digraph as the authoritative instruction source.\nDo not invent nodes, edges, or steps not present in the graph. When a step is ambiguous, ask one\nclarification and halt.\n\nHard rules:\n- Open with a concise 3–7 bullet CHECKLIST of conceptual steps derived from the digraph’s structure.\n- Before any interpretation, emit a PURPOSE_AND_INPUTS section that states the task purpose and the key inputs extracted from node/edge labels/attributes.\n- Execute node-by-node consistent with the digraph, emitting a STEP_k block per major step. After each step, include a brief VALIDATE line (pass/fail and reason). If fail, self-correct once or mark blocked.\n- Never operate outside the digraph. If an action is not represented by a node/edge, refuse and ask for an updated graph.\n- Keep reasoning terse. No chain-of-thought. Only minimal justifications in validation lines.\n\nOutput contract (strict section order):\n1) CHECKLIST\n2) PURPOSE_AND_INPUTS\n3) STEP_k blocks (k = 1..N)\n4) SUMMARY\n5) ARTIFACT (optional if a file/script is produced)\n\nSTEP block format (must match exactly):\nSTEP_k: <node_id> "<node_label>"\n- ACTION: <1–2 lines strictly within the node scope>\n- RESULT_JSON:\n{\n  "node_id": "<node_id>",\n  "status": "ok" | "corrected" | "blocked",\n  "evidence": "<≤200 chars>",\n  "next_candidates": ["<neighbor_id_1>", "..."]\n}\n- VALIDATE: <≤1 line: pass/fail + reason>\n\nProgression rules:\n- Allowed next nodes are the outgoing neighbors of the current node.\n- Do not skip nodes required by edge connectivity.\n- If multiple branches exist, choose one and justify in VALIDATE using edge labels/conditions. If indecisive from DOT, set status="blocked" and halt with a single clarification question.\n\nRefusal rule:\nIf the DOT is malformed, has no entry node (in-degree 0), or is cyclic without any terminal condition where a terminal is required, emit only:\nERROR_JSON:\n{"error":"dot_unusable","reason":"<brief>","required_fix":"<brief>"}\n\nRESULT_JSON schema (for validation tools):\n{\n  "type":"object",\n  "properties":{\n    "node_id":{"type":"string"},\n    "status":{"type":"string","enum":["ok","corrected","blocked"]},\n    "evidence":{"type":"string","maxLength":200},\n    "next_candidates":{"type":"array","items":{"type":"string"}}\n  },\n  "required":["node_id","status","evidence","next_candidates"],\n  "additionalProperties":false\n}'), ChatMessage(role='user', content='Graphviz DOT code:\n\n                    ```\n\n                    digraph MultiAgentWorkflow {\n    rankdir=LR;\n    node [shape=box, fontsize=10];\n\n    subgraph cluster_0 {\n        label="Stage 1: User Request";\n        style=dashed;\n        UserRequest [label="User Request\\n(VS Code Active Document)"];\n    }\n\n    subgraph cluster_1 {\n        label="Stage 2: Planning";\n        Plan [label="Break Down Problem\\nSequential Thinking"];\n        TodoList [label="Create Todo List\\n(Markdown)"];\n    }\n\n    subgraph cluster_2 {\n        label="Stage 3: Research";\n        InternetSearch [label="Internet Search\\n(Google via fetch_webpage)"];\n        FetchURLs [label="Fetch URLs\\n(Recursively)"];\n        Filtering [label="Filtering\\n(Relevant Info Only)"];\n        Summarisation [label="Summarisation\\n(Condense Findings)"];\n    }\n\n    subgraph cluster_3 {\n        label="Stage 4: Codebase Investigation";\n        ExploreFiles [label="Explore Files\\n(Search Functions, Classes)"];\n        GatherContext [label="Gather Context\\n(2000 lines at a time)"];\n    }\n\n    subgraph cluster_4 {\n        label="Stage 5: Implementation";\n        CodeChange [label="Code Changes\\n(Small, Incremental)"];\n        Debug [label="Debugging\\n(get_errors, Print Statements)"];\n        Test [label="Testing\\n(Run Unit Tests, Output Pane)"];\n    }\n\n    subgraph cluster_5 {\n        label="Stage 6: Validation & QA";\n        Validate [label="Validate Solution\\n(Edge Cases, Hidden Tests)"];\n        Reflect [label="Reflect & Iterate\\n(Additional Tests)"];\n        Complete [label="Complete\\n(All Todo Items Checked Off)"];\n    }\n\n    % Workflow edges\n    UserRequest -> Plan -> TodoList -> InternetSearch;\n    InternetSearch -> FetchURLs -> Filtering -> Summarisation;\n    Summarisation -> ExploreFiles -> GatherContext -> CodeChange;\n    CodeChange -> Debug -> Test -> Validate -> Reflect -> Complete;\n\n    % Validation/QA loops\n    Validate -> Debug [label="If issues found", style=dotted, color=red];\n    Reflect -> InternetSearch [label="If more info needed", style=dotted, color=blue];\n    Test -> CodeChange [label="If tests fail", style=dotted, color=red];\n\n    % Internet access, filtering, summarisation interactions\n    InternetSearch -> Filtering [label="Filter results", style=bold];\n    Filtering -> Summarisation [label="Summarise findings", style=bold];\n\n    % Feedback paths\n    Complete -> UserRequest [label="Yield back to user", style=dashed];\n\n    % Annotations\n    InternetSearch [color=green, style=filled, fillcolor=lightyellow];\n    Filtering [color=orange, style=filled, fillcolor=lightgrey];\n    Summarisation [color=blue, style=filled, fillcolor=lightblue];\n    Validate [color=red, style=filled, fillcolor=pink];\n}\n\n                    ```\n\n                    # OUTPUT FORMAT\n                    - CHECKLIST: bullet list.\n                    - PURPOSE_AND_INPUTS: two short lines: Purpose: … / Inputs: …\n                    - STEP_k blocks as defined in the System prompt.\n                    - SUMMARY: one short paragraph summarizing what was done, which terminal condition was met, and any anomalies.\n                    - ARTIFACT: include only if you output a file/script; otherwise omit.\n\n                    # COMPLIANCE\n                    Follow these instructions exactly. Do not deviate from the section order or formats.')]
```
}
