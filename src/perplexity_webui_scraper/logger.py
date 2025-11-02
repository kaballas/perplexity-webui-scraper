"""
Logging configuration for the Perplexity WebUI Scraper.

This module provides configurable logging capabilities with different levels,
formatters, and output options.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }

    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logger(
    name: str = "perplexity_webui_scraper",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    enable_colors: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with the specified configuration.

    Args:
        name: Logger name (default: "perplexity_webui_scraper")
        level: Logging level (default: logging.INFO)
        log_file: Optional path to log file for file output
        enable_colors: Whether to enable colored output for console (default: True)
        format_string: Custom format string (optional)

    Returns:
        Configured logger instance
    """

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Default format string
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if enable_colors and sys.stdout.isatty():
        console_formatter = ColoredFormatter(format_string)
    else:
        console_formatter = logging.Formatter(format_string)

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "perplexity_webui_scraper") -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        logger = setup_logger(name)

    return logger


def set_debug_level(logger_name: str = "perplexity_webui_scraper") -> None:
    """
    Set logger to DEBUG level for verbose output.

    Args:
        logger_name: Name of the logger to modify
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Update all handlers to DEBUG level
    for handler in logger.handlers:
        handler.setLevel(logging.DEBUG)


def log_request_details(logger: logging.Logger, method: str, url: str,
                       headers: Optional[dict] = None, data: Optional[dict] = None,
                       params: Optional[dict] = None) -> None:
    """
    Log HTTP request details at DEBUG level.

    Args:
        logger: Logger instance
        method: HTTP method
        url: Request URL
        headers: Request headers (optional, sensitive data will be masked)
        data: Request data (optional, will be truncated if too long)
        params: URL parameters (optional)
    """
    # Build full URL with params for logging
    full_url = url
    if params:
        param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{param_str}"

    logger.debug(f"HTTP Request: {method} {full_url}")

    if params:
        logger.debug(f"Request params: {params}")

    if headers:
        # Mask sensitive headers
        safe_headers = {}
        for key, value in headers.items():
            if any(sensitive in key.lower() for sensitive in ['auth', 'token', 'cookie', 'key']):
                safe_headers[key] = '[MASKED]'
            else:
                safe_headers[key] = value
        logger.debug(f"Request headers: {safe_headers}")

    if data:
        # Truncate large data payloads
        data_str = str(data)
        if len(data_str) > 500:
            data_str = data_str[:500] + '... [TRUNCATED]'
        logger.debug(f"Request data: {data_str}")


def log_response_details(logger: logging.Logger, status_code: int,
                        response_data: Optional[dict] = None, truncate_at: int = 1000) -> None:
    """
    Log HTTP response details at DEBUG level.

    Args:
        logger: Logger instance
        status_code: HTTP status code
        response_data: Response data (optional, will be truncated if too long)
        truncate_at: Maximum length for response data logging
    """
    logger.debug(f"HTTP Response: Status {status_code}")

    if response_data:
        data_str = str(response_data)
        if len(data_str) > truncate_at:
            data_str = data_str[:truncate_at] + '... [TRUNCATED]'
        logger.debug(f"Response data: {data_str}")
