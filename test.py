import json
import time
from pathlib import Path
from os import getenv
from dotenv import load_dotenv
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich.progress import Progress, TaskID

from perplexity_webui_scraper import Perplexity, CitationMode, ModelType, SearchFocus, SourceFocus, TimeRange

# Load environment variables
load_dotenv()

# Setup console for rich output
console = Console()

console.print("[bold blue]Perplexity WebUI Scraper - JSONL Batch Processor[/bold blue]")
console.print()

# File paths
input_file = Path("C:\\DTT\\work\\perplexity-webui-scraper\\data\\sap_question.jsonl")
output_file = Path("C:\\DTT\\work\\perplexity-webui-scraper\\data\\sap_question_processed.jsonl")

# Debug: Check session token
session_token = getenv("PERPLEXITY_SESSION_TOKEN")
console.print(f"[yellow]Session token exists:[/yellow] {'Yes' if session_token else 'No'}")
if session_token:
    console.print(f"[yellow]Session token length:[/yellow] {len(session_token)}")

# Create client
try:
    client = Perplexity(session_token=session_token)
    console.print("[green]✓ Perplexity client created successfully[/green]")
except Exception as e:
    console.print(f"[red]Error creating Perplexity client: {e}[/red]")
    exit(1)

# Research strategist prompt for generating research questions
research_strategist_prompt = """## Role
Deliver clarity and stepwise reasoning. Objective: Enable independent, high-fidelity cognition.

## HARD RULES
- Output is direct, blunt, instructional. No sentiment. No filler.
- Begin every reply with a <think>…</think> block (≤6 lines: objective, assumptions, plan, risks, scope).
- Provide a 3–7 item checklist immediately after the scratchpad.
- Use strict section headings with IDs: S1 UNDERSTAND, S2 ANALYZE, S3 REASON, S4 SYNTHESIZE, S5 VALIDATE, S6 DELIVER (only those needed).
- When code is involved, include full, self-contained code blocks.
- **All text must use Australian English spelling, grammar, and conventions. American English is not permitted.**

## WORKFLOW (CANONICAL LOOP)
1) UNDERSTAND: Restate task and constraints in ≤2 lines.
2) ANALYZE: List conflicts, unknowns, and constraints; bullet form only.
3) REASON: State decisions and trade-offs; bullet form only.
4) SYNTHESIZE: Produce the artifact or answer.
5) VALIDATE: In ≤2 lines, run binary checks against acceptance criteria.
(If needed) 6) DELIVER: Provide next actions or a minimal template.

## REASONING STRUCTURE
- Use: Attention → Extraction → Operations → Pathway → Steps → Metacognition.
- Questions: Provide ≥5 only when discovery is required or blockers exist; otherwise omit to preserve brevity.

## AFFECTIVE SUPPRESSION
- No engagement language. No hedging. No flattery.

## PLANNING & VERIFICATION
- Dissect requests; track assumptions inline.
- Validate with explicit binary checks (e.g., “Checklist included: Yes/No”).
- Self-correct immediately if a rule is violated; note correction in VALIDATE.

## OUTPUT FORMAT
- Always include the scratchpad and a 3–7 item checklist.
- Headings/IDs exactly as specified.
- Tight bullets. No narratives beyond what is necessary to execute.

## VERBOSITY LIMITS
- Target ≤400 words unless code or tabular data requires more.
- Prioritise the deliverable over commentary when limits collide.

## STOP CONDITIONS
- Stop when the deliverable is provided and required sections are present.
- If unknowns block completion, deliver partial output + “Open Questions” then stop.

## EXCEPTIONS
- If platform/policy forbids private chain-of-thought, restrict scratchpad to public meta (objective/assumptions/plan). No internal reasoning disclosure.

## ENFORCEMENT
- Absolute adherence. If any rule conflicts, precedence order: Safety/Policy > Deliverable > Required Sections > Verbosity.

"""

def process_single_record(record, record_num, total_records):
    """Process a single JSONL record through the two-step research approach"""

    # Create task-specific prompt
    task_prompt = f"""\n\n\n Your Task: {record.get('Title', 'Unknown Title')}

Description: {record.get('Description', 'No description available')}

Area: {record.get('Area', [])}
Product: {record.get('Product', [])}
See More Link: {record.get('SeeMoreLink', 'No link available')}"""

    # Step 1: Generate research instructions
    console.print(f"[cyan]Record {record_num}/{total_records}:[/cyan] [green]Step 1 - Generating research plan...[/green]")

    full_strategist_prompt = research_strategist_prompt
    full_strategist_prompt += task_prompt

    # DEBUG: Print the prompt and exit
    console.print("[yellow]DEBUG: Full prompt generated successfully[/yellow]")
    console.print(f"[yellow]Prompt length: {len(full_strategist_prompt)} characters[/yellow]")

    research_instructions = None
    with Live(Panel("", title=f"Record {record_num}: Generating Research Plan", border_style="white"), refresh_per_second=10) as live:
        for chunk in client.ask(
            query=full_strategist_prompt,
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
            if chunk.last_chunk:
                research_instructions = chunk.answer or "No research plan generated"
                live.update(Panel(f"Research plan generated ({len(research_instructions)} chars)",
                                title=f"Record {record_num}: Research Plan Complete", border_style="green"))

    # Wait 30 seconds before next request
    console.print(f"[yellow]Waiting 30 seconds before executing research...[/yellow]")
    time.sleep(30)

    # Step 2: Execute research
    console.print(f"[cyan]Record {record_num}/{total_records}:[/cyan] [green]Step 2 - Executing research...[/green]")

    final_research_report = None
    with Live(Panel("", title=f"Record {record_num}: Conducting Research", border_style="white"), refresh_per_second=10) as live:
        for chunk in client.ask(
            query=research_instructions,
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
            if chunk.last_chunk:
                final_research_report = chunk.answer or "No research completed"
                live.update(Panel(f"Research completed ({len(final_research_report)} chars)",
                                title=f"Record {record_num}: Research Complete", border_style="green"))

    # Add research results to the record
    record['research_instructions'] = research_instructions
    record['research_report'] = final_research_report
    record['processed'] = True

    return record

def main():
    """Main processing function"""
    console.print(f"[yellow]Input file:[/yellow] {input_file}")
    console.print(f"[yellow]Output file:[/yellow] {output_file}")

    # Debug: Check if files exist
    console.print(f"[yellow]Input file exists:[/yellow] {'Yes' if input_file.exists() else 'No'}")
    if input_file.exists():
        console.print(f"[yellow]Input file size:[/yellow] {input_file.stat().st_size} bytes")

    console.print()

    # Check if input file exists
    if not input_file.exists():
        console.print(f"[red]Error: Input file not found: {input_file}[/red]")
        return

    # Check if output file already exists and ask about resuming
    resume_from = 0
    if output_file.exists():
        console.print(f"[yellow]Output file already exists. Checking for completed records...[/yellow]")
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_lines = f.readlines()
                resume_from = len(existing_lines)
                console.print(f"[green]Found {resume_from} completed records. Will resume from record {resume_from + 1}[/green]")
        except Exception as e:
            console.print(f"[red]Error reading existing output file: {e}[/red]")
            console.print("[yellow]Starting fresh...[/yellow]")
            resume_from = 0

    # Read and process records
    processed_records = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total_records = len(lines)

            console.print(f"[green]Found {total_records} total records to process[/green]")

            if resume_from > 0:
                console.print(f"[blue]Resuming from record {resume_from + 1}[/blue]")
                lines_to_process = lines[resume_from:]
                start_index = resume_from + 1
            else:
                lines_to_process = lines
                start_index = 1

            console.print(f"[green]Processing {len(lines_to_process)} remaining records[/green]")
            console.print()

            for i, line in enumerate(lines_to_process, start_index):
                try:
                    # Parse JSON record
                    record = json.loads(line.strip())

                    console.print(f"[blue]Processing record {i}/{total_records}: {record.get('Title', 'Unknown')[:60]}...[/blue]")

                    # Process the record
                    processed_record = process_single_record(record, i, total_records)
                    processed_records.append(processed_record)

                    # Append to output file immediately (for resume capability)
                    with open(output_file, 'a', encoding='utf-8') as out_f:
                        out_f.write(json.dumps(processed_record, ensure_ascii=False) + '\n')

                    console.print(f"[green]✓ Record {i} completed and saved[/green]")

                    # Wait 30 seconds before processing next record (except for the last record)
                    if i < total_records:
                        console.print(f"[yellow]Waiting 30 seconds before next record...[/yellow]")
                        time.sleep(30)

                    # Progress update every 5 records
                    if i % 5 == 0:
                        progress_pct = (i / total_records) * 100
                        console.print(f"[blue]Progress: {i}/{total_records} ({progress_pct:.1f}%) records completed[/blue]")

                    console.print()

                except json.JSONDecodeError as e:
                    console.print(f"[red]Error parsing line {i}: {e}[/red]")
                    continue
                except Exception as e:
                    console.print(f"[red]Error processing record {i}: {e}[/red]")
                    console.print("[yellow]Continuing with next record...[/yellow]")
                    continue

            final_count = resume_from + len(processed_records)
            console.print(f"[green]✓ Batch processing completed! {final_count}/{total_records} total records processed[/green]")
            console.print(f"[green]✓ Results saved to {output_file}[/green]")

            # Show some stats
            if processed_records:
                avg_research_length = sum(len(r.get('research_report', '')) for r in processed_records) / len(processed_records)
                console.print(f"[cyan]Average research report length: {avg_research_length:.0f} characters[/cyan]")

    except Exception as e:
        console.print(f"[red]Error reading input file: {e}[/red]")
        return

if __name__ == "__main__":
    main()
