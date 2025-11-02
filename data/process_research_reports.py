import argparse
import json
from pathlib import Path
import pyttsx3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Display each research_report entry from a JSONL file and prompt for "
            "whether to create a blog post."
        )
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        default="sap_question_processed.jsonl",
        help="Path to the JSON Lines file to process.",
    )
    return parser.parse_args()


def prompt_decision(record_number: int, report: str) -> str:
    while True:
        choice = input(
            "Create blog post for this research_report? [y]es/[n]o/[q]uit/[p]layback: "
        ).strip().lower()
        if choice in {"y", "n", "q"}:
            return choice
        elif choice == "p":
            play_text(report)
        else:
            print("Please respond with 'y', 'n', 'q' to quit, or 'p' to playback.")
def play_text(text: str) -> None:
    """Play back the given text using pyttsx3."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def process_file(path: Path) -> None:
    if not path.exists():
        print(f"File not found: {path}")
        return

    with path.open(encoding="utf-8") as handle:
        for record_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"Skipping line {record_number}: {exc}")
                continue

            report = record.get("research_report")
            if not report:
                print(f"Skipping line {record_number}: no research_report field present.")
                continue

            separator = "=" * 80
            print(separator)
            print(f"Record {record_number}")
            print(separator)
            print(report)
            print()

            decision = prompt_decision(record_number, report)
            if decision == "q":
                print("Stopping at user request.")
                break

            outcome = "Create blog post" if decision == "y" else "Do not create blog post"
            print(f"Decision recorded: {outcome}.\n")
        else:
            print("Reached end of file.")


def main() -> None:
    args = parse_args()
    process_file(Path(args.input_path).expanduser())


if __name__ == "__main__":
    main()
