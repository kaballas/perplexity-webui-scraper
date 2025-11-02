"""
Advanced debug example for Perplexity WebUI Scraper

This script demonstrates various debugging scenarios and capabilities.
"""

import logging
from os import getenv
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from perplexity_webui_scraper import Perplexity, CitationMode, ModelType, SearchFocus, SourceFocus, TimeRange
from perplexity_webui_scraper.logger import setup_logger, set_debug_level

# Load environment variables
load_dotenv()

# Setup console for rich output
console = Console()

def demo_logging_levels():
    """Demonstrate different logging levels."""
    console.print("[bold blue]=== Logging Levels Demo ===[/bold blue]")

    # Create a table to show logging levels
    table = Table(title="Available Logging Levels")
    table.add_column("Level", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_column("Description", style="green")

    table.add_row("CRITICAL", "50", "Only critical errors")
    table.add_row("ERROR", "40", "Error messages")
    table.add_row("WARNING", "30", "Warning messages")
    table.add_row("INFO", "20", "General information")
    table.add_row("DEBUG", "10", "Detailed debug information")

    console.print(table)
    console.print()

    # Demo each level
    levels = [
        (logging.ERROR, "ERROR"),
        (logging.WARNING, "WARNING"),
        (logging.INFO, "INFO"),
        (logging.DEBUG, "DEBUG")
    ]

    for level, name in levels:
        console.print(f"[yellow]Setting log level to {name}:[/yellow]")
        logger = setup_logger(level=level)

        # Create a simple client to trigger some logging
        console.print(f"Creating client with {name} level...")
        client = Perplexity(session_token=getenv("PERPLEXITY_SESSION_TOKEN"))
        console.print("✓ Client created")
        console.print()


def demo_file_logging():
    """Demonstrate file logging capabilities."""
    console.print("[bold blue]=== File Logging Demo ===[/bold blue]")

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "perplexity_debug.log"
    console.print(f"[green]Setting up file logging to: {log_file}[/green]")

    # Setup logger with file output
    logger = setup_logger(
        level=logging.DEBUG,
        log_file=str(log_file),
        enable_colors=False  # Colors don't work well in files
    )

    console.print("✓ File logger configured")

    # Create client and make a simple query to generate logs
    client = Perplexity(session_token=getenv("PERPLEXITY_SESSION_TOKEN"))

    console.print("Making a simple query to generate log entries...")
    try:
        response = client.ask(
            query="What is Python?",
            model=ModelType.Sonar,
            citation_mode=CitationMode.CLEAN
        ).run()

        console.print(f"✓ Query completed - Answer length: {len(response.answer) if response.answer else 0} characters")

        # Show log file info
        if log_file.exists():
            file_size = log_file.stat().st_size
            console.print(f"✓ Log file created: {file_size} bytes")
            console.print(f"📁 Log location: {log_file.absolute()}")

    except Exception as e:
        console.print(f"[red]Error during query: {e}[/red]")

    console.print()


def demo_error_scenarios():
    """Demonstrate error handling with debug information."""
    console.print("[bold blue]=== Error Scenarios Demo ===[/bold blue]")

    # Setup debug logging
    logger = setup_logger(level=logging.DEBUG)
    client = Perplexity(session_token=getenv("PERPLEXITY_SESSION_TOKEN"))

    # Test 1: Invalid file
    console.print("[yellow]1. Testing with non-existent file:[/yellow]")
    try:
        client.ask(
            query="Analyze this file",
            files=["non_existent_file.txt"]
        ).run()
    except Exception as e:
        console.print(f"✓ Caught expected error: {type(e).__name__}")

    # Test 2: Too many files (simulate)
    console.print("[yellow]2. Testing file validation logging:[/yellow]")
    # Create a temporary file for testing
    temp_file = Path("temp_test.txt")
    temp_file.write_text("This is a test file for debugging.")

    try:
        validated_files = client.validate_files([str(temp_file)])
        console.print(f"✓ File validation completed: {len(validated_files)} files")
    except Exception as e:
        console.print(f"✓ Validation error: {e}")
    finally:
        # Cleanup
        if temp_file.exists():
            temp_file.unlink()

    console.print()


def demo_performance_logging():
    """Demonstrate performance-related logging."""
    console.print("[bold blue]=== Performance Logging Demo ===[/bold blue]")

    import time

    # Setup debug logging
    logger = setup_logger(level=logging.DEBUG)
    client = Perplexity(session_token=getenv("PERPLEXITY_SESSION_TOKEN"))

    console.print("Making a query with timing information...")
    start_time = time.time()

    try:
        chunk_count = 0
        for chunk in client.ask(
            query="Explain quantum computing in simple terms",
            model=ModelType.Best,
            citation_mode=CitationMode.MARKDOWN
        ).stream():
            chunk_count += 1
            if chunk.last_chunk:
                break

        end_time = time.time()
        duration = end_time - start_time

        console.print(f"✓ Query completed in {duration:.2f} seconds")
        console.print(f"✓ Received {chunk_count} chunks")
        console.print(f"✓ Average time per chunk: {duration/chunk_count:.3f} seconds")

    except Exception as e:
        console.print(f"[red]Error during performance test: {e}[/red]")

    console.print()


def main():
    """Run all debug demonstrations."""
    console.print("[bold green]Perplexity WebUI Scraper - Advanced Debug Demo[/bold green]")
    console.print()

    # Check if session token is available
    session_token = getenv("PERPLEXITY_SESSION_TOKEN")
    if not session_token:
        console.print("[red]ERROR: PERPLEXITY_SESSION_TOKEN environment variable not found![/red]")
        console.print("Please set your session token before running this demo.")
        return

    console.print(f"✓ Session token found: {'*' * 8}{session_token[-4:]}")
    console.print()

    try:
        # Run all demos
        demo_logging_levels()
        demo_file_logging()
        demo_error_scenarios()
        demo_performance_logging()

        console.print("[bold green]All demos completed successfully![/bold green]")
        console.print()
        console.print("[cyan]Debug features demonstrated:[/cyan]")
        console.print("• Multiple logging levels (ERROR, WARNING, INFO, DEBUG)")
        console.print("• File output with timestamps and formatting")
        console.print("• Error handling and validation logging")
        console.print("• HTTP request/response details")
        console.print("• Data processing and parsing steps")
        console.print("• Performance and timing information")
        console.print("• Citation processing details")
        console.print("• Model selection logging")

    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
