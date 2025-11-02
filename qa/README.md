# Perplexity Harness (QA Module)

This folder houses the modularised test harness that drives Perplexity WebUI Scraper test runs. The former single-file script (`test_small.py`) is now a thin shim that imports the package entry point so that the command-line UX remains identical while the maintainable implementation lives under `pplx_harness/`.

## Quick Start

```bash
cd qa
python -m pplx_harness --max-records 5
```

Or use the SAP SuccessFactors Debate Orchestrator:

```bash
cd qa
python -m debate "Discuss SuccessFactors Employee Central implementation"
```

Environment variables (read via `python-dotenv`) still control defaults:

- `PERPLEXITY_SESSION_TOKEN` - required, authenticates the API client.
- `PPLX_INPUT` / `PPLX_OUTPUT` - optional overrides for JSONL input/output paths.
- `PPLX_MAX_RECORDS` - optional default for record cap (overridden by CLI flag).
- `WRICEF_API_TOKEN` - required for HuggingFace-based agents in the debate orchestrator.

### SAP SuccessFactors Debate Orchestrator

The repository also includes a sophisticated multi-agent debate orchestrator designed for SAP SuccessFactors implementation discussions. See `debate/README.md` for comprehensive documentation on its 21 specialized agents and advanced features.

Typical usage:

```bash
python -m debate "Design an integration between SuccessFactors and SAP S/4HANA"
```

Key features:
- 21 specialized agents (Solution Architect, Fact Checker, Technical Writer, etc.)
- Multi-round conversations with user interaction
- Quality assurance and peer review capabilities
- Conversation compression and context management
- Automatic transcript generation
- Task management with TodoAgent
- Per-agent configuration and customization

See `debate/README.md` for complete documentation.

### WRICEF Prompt Utility

The repo now ships `generate_wricef_prompts.py`, a helper for building and validating WRICEF prompt content outside the main harness.

Typical usage:

```bash
python generate_wricef_prompts.py data/sap_question_test.json \
  --output results.json \
  --api-token "$WRICEF_API_TOKEN" \
  --resume \
  --max-records 25
```

Key behaviours:

- **Gating:** the WRICEF template enforces a configuration-first checklist. If a requirement can be met purely through standard SuccessFactors configuration, the script returns the sentinel response (`1. No WRICEF components required...`) instead of fabricating deliverables.
- **Resume support:** add `--resume` (requires `--output`) to skip records whose IDs already exist in the output file. The script persists a `wricef_record_key` based on `id`/`requirement`/`Title`, so subsequent runs avoid reprocessing the same item.
- **Targeted reprocessing:** supply `--reprocess-index N` with `--output` to replace a previously processed record by its `wricef_index`. The input record is re-run and its result overwrites the stored entry while other rows remain untouched.
- **QA review loop:** use `--review-index N` (with `--output` and an API token) to ask the model to review an existing WRICEF deliverable. Passing `0` reviews every record that has not yet been reviewed (based on the `wricef_record_key`); subsequent runs only pick up new or reprocessed items. Review details are saved on the same record under `wricef_review`.
- **API calls:** provide `--api-token` (or set `WRICEF_API_TOKEN`) to collect completions from the DOE Tender proxy. To run prompt generation offline, omit the token or pass `--allow-anonymous`.
- **Record caps:** `--max-records` limits the number of inputs processed on each run, which is useful for quick smoke checks against large JSON dumps.

Outputs are merged with any existing JSON/JSONL file when `--resume` is active, and the CLI echoes progress to stdout when no output file is supplied.

## Package Layout

```
pplx_harness/
├── __main__.py          # enables `python -m pplx_harness`
├── cli.py               # CLI orchestration and console wiring
├── config.py            # env loading, arg parsing, client creation
├── constants.py         # sentinel text, defaults, allowed sets
├── types.py             # Protocols and RunConfig dataclass
├── io/
│   └── jsonl.py         # ensure sample input, JSONL read/write
├── prompts/
│   ├── restrictive.py   # restrictive prompt template + formatter
│   └── wricef.py        # WRICEF template with gating checklist
├── text/
│   ├── regexes.py       # shared compiled regexes
│   └── sentences.py     # deterministic first-sentence extractor
├── gating/
│   ├── topics.py        # topic keyword map + classifier
│   ├── compliance.py    # compliance vocabulary helpers
│   └── enforce.py       # topic/compliance gating logic
├── sanitize/
│   └── limitations.py   # numbered list sanitisation + validation extraction
├── net/
│   ├── pplx.py          # Perplexity adapter + streaming collector
│   └── rewriter.py      # optional human-readable rewrite helpers
├── validate/
│   ├── evidence.py      # authoritative URL + module normalisation
│   └── records.py       # final record validation & metrics
└── processing/
    └── pipeline.py      # process_single_record/process_records orchestrator

ui/
└── console.py           # Rich console wrappers (optional in tests)

debate/                  # SAP SuccessFactors Debate Orchestrator
├── __init__.py          # Package initialization
├── __main__.py          # Main entry point
├── agents.py           # Agent implementations (21 specialized agents)
├── cli.py              # Command-line interface
├── clients.py          # API client implementations
├── core.py             # Core debate orchestration
├── prompts.py          # Agent prompt templates
└── README.md           # Comprehensive documentation
```

Top-level `tests/` cover prompt generation, sanitisation, validation, WRICEF CLI scenarios, and a pipeline smoke case. `test_small.py` simply points to `pplx_harness.cli:main`, preserving existing entry points.

## Control Flow

1. **CLI (`cli.py:29`)** loads `.env`, parses CLI args, establishes the Perplexity client, and builds callbacks for Rich output.
2. **Config (`config.py:39`)** returns a `RunConfig` populated with resolved paths, max record count, and the `PplxAdapter`.
3. **I/O (`io/jsonl.py:25`)** creates sample data on demand, reads JSONL records (respecting the record cap), and writes results.
4. **Processing (`processing/pipeline.py:58`)** drives each record:
   - builds the restrictive prompt (`prompts/restrictive.py:72`)
   - streams or falls back to a single response via `net/pplx.py:90`
   - sanitises limitations (`sanitize/limitations.py:93`) and optionally rewrites human-readable text (`net/rewriter.py:162`)
   - validates the final record (`validate/records.py:19`)
5. **Console (`ui/console.py:9`)** wrappers keep Rich usage isolated so the pipeline can run headless during unit tests.

## Development Workflow

1. **Environment** - ensure dependencies from the parent project are installed (Rich, python-dotenv, requests, pytest).
2. **Refactoring** - add new logic in the dedicated module that matches its responsibility (e.g., new gating rules in `gating/`).
3. **Injection** - pass new collaborators into `process_single_record` via arguments/config rather than adding globals.
4. **Testing** - create focused tests in `tests/` and run `pytest` from `qa/`; tests already mock network traffic.
5. **Validation** - keep default behaviour parity by using immutable helpers and verifying JSON/JSONL diffs when touching pipeline logic.

## Extension Guidelines

- **New prompt variants:** create a sibling in `prompts/` and dispatch from the pipeline behind a feature flag or config knob.
- **Alternative clients:** implement the `PplxClient` protocol (`types.py:9`) and inject through `config.create_client`.
- **UI changes:** restrict console output to `ui/console.py` to preserve testability.
- **Sanitisation tweaks:** keep pure utilities in `sanitize/` and share text helpers via `text/`.
- **WRICEF enhancements:** extend `prompts/wricef.py` gating rules or CLI behaviour (`generate_wricef_prompts.py`) to capture additional resume keys, output schemas, or validation checks.

Keeping modules small and dependency-injected preserves the original harness behaviour while making it easier for developers to reason about and extend. Run `pytest` after any change to confirm the core flow stays intact.
