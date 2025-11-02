"""
Simple example of saving debug output to a log file.

This script demonstrates how to set up file logging for the Perplexity WebUI Scraper.
"""

import logging
from os import getenv
from pathlib import Path
from dotenv import load_dotenv

from perplexity_webui_scraper import Perplexity, CitationMode, ModelType
from perplexity_webui_scraper.logger import setup_logger

# Load environment variables
load_dotenv()

def main():
    print("Perplexity WebUI Scraper - File Logging Example")
    print("=" * 50)

    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Setup logger with file output
    log_file = logs_dir / "simple_debug.log"
    logger = setup_logger(
        level=logging.DEBUG,
        log_file=str(log_file),
        enable_colors=False  # No colors in file output
    )

    print(f"✓ Logger configured with DEBUG level")
    print(f"✓ Log file: {log_file.absolute()}")
    print()

    # Create client and make a query
    print("Creating Perplexity client...")
    client = Perplexity(session_token=getenv("PERPLEXITY_SESSION_TOKEN"))
    print("✓ Client created")
    print()

    print("Making a simple query...")
    logger.info("Starting example query for file logging demonstration")

    try:
        response = client.ask(
            query="What is Python programming language?",
            citation_mode=CitationMode.MARKDOWN,
            model=ModelType.Sonar
        ).run()

        print(f"✓ Query completed successfully")
        print(f"✓ Answer length: {len(response.answer) if response.answer else 0} characters")
        print(f"✓ Search results: {len(response.search_results)}")
        print()

        # Show log file information
        if log_file.exists():
            file_size = log_file.stat().st_size
            print(f"✓ Debug log saved: {log_file}")
            print(f"✓ File size: {file_size:,} bytes")

            # Count lines in log file
            with open(log_file, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            print(f"✓ Log entries: {line_count} lines")
            print()

            # Show sample of log content
            print("Sample log entries:")
            print("-" * 30)
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show first 3 and last 3 lines
                for i, line in enumerate(lines[:3]):
                    print(f"{i+1:3d}: {line.rstrip()}")

                if len(lines) > 6:
                    print("    ... (more entries in between)")
                    for i, line in enumerate(lines[-3:], len(lines)-2):
                        print(f"{i:3d}: {line.rstrip()}")

            print("-" * 30)
            print()
            print("To view the complete log file:")
            print(f"  Windows: type {log_file}")
            print(f"  Unix:    cat {log_file}")

        else:
            print("❌ Log file was not created")

    except Exception as e:
        print(f"❌ Error during query: {e}")
        logger.error(f"Query failed: {e}")


if __name__ == "__main__":
    main()
