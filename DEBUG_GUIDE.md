# Debug Information Guide

This document provides a comprehensive guide on the debug information capabilities added to the Perplexity WebUI Scraper.

## Overview

The scraper now includes extensive debug logging throughout the codebase to help developers understand what's happening during execution, troubleshoot issues, and monitor performance.

## Quick Start

### Basic Debug Setup

```python
from perplexity_webui_scraper import Perplexity, setup_logger, set_debug_level
import logging

# Setup logger with INFO level (default)
logger = setup_logger()

# Create client (will log initialization details)
client = Perplexity(session_token="your-session-token")

# Enable detailed DEBUG logging
set_debug_level()

# Make a request (will log detailed execution info)
response = client.ask("What is machine learning?").run()
```

### File Logging

```python
from perplexity_webui_scraper import setup_logger
import logging

# Log to both console and file
logger = setup_logger(
    level=logging.DEBUG,
    log_file="debug.log",
    enable_colors=True  # Colors for console, plain text for file
)
```

## Logging Levels

The scraper supports standard Python logging levels:

| Level | Value | Description | Use Case |
|-------|-------|-------------|----------|
| `DEBUG` | 10 | Very detailed information | Development, troubleshooting |
| `INFO` | 20 | General operational information | Normal usage monitoring |
| `WARNING` | 30 | Warning messages | Potential issues |
| `ERROR` | 40 | Error messages | Error handling |
| `CRITICAL` | 50 | Critical errors | System failures |

### Setting Levels

```python
import logging
from perplexity_webui_scraper import setup_logger, set_debug_level

# Set specific level during setup
logger = setup_logger(level=logging.WARNING)

# Change to DEBUG level after setup
set_debug_level()

# Use standard logging levels
logger = setup_logger(level=logging.INFO)
```

## What Gets Logged

### Client Initialization
- Session token validation (masked for security)
- HTTP client configuration
- Headers and timeout settings
- File upload limits

### File Processing
- File validation steps
- MIME type detection
- Size and permission checks
- Upload URL generation
- Upload progress

### Request Processing
- Query preparation
- Model selection
- Parameter validation
- HTTP request details (with sensitive data masked)
- JSON payload structure

### Response Processing
- Stream connection establishment
- Data chunk processing
- JSON parsing steps
- Citation formatting
- Search result extraction

### Error Handling
- Detailed error context
- File access issues
- Network problems
- Parsing failures

## Configuration Options

### Custom Logger Setup

```python
from perplexity_webui_scraper.logger import setup_logger
import logging

logger = setup_logger(
    name="my_app",                    # Custom logger name
    level=logging.DEBUG,              # Logging level
    log_file="logs/debug.log",        # Optional file output
    enable_colors=True,               # Colored console output
    format_string="%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # Custom format
)
```

### Multiple Loggers

```python
# Different loggers for different components
main_logger = setup_logger("main_app", level=logging.INFO)
debug_logger = setup_logger("debug", level=logging.DEBUG, log_file="debug.log")

# Use specific logger
from perplexity_webui_scraper.logger import get_logger
logger = get_logger("main_app")
```

## Debug Output Examples

### INFO Level Output
```
2024-01-01 10:00:00 - perplexity_webui_scraper - INFO - Initializing Perplexity client
2024-01-01 10:00:01 - perplexity_webui_scraper - INFO - Starting ask request with query: What is machine learning?
2024-01-01 10:00:02 - perplexity_webui_scraper - INFO - Ask request completed - Answer: 1250 chars, Search results: 5, Chunks: 3
```

### DEBUG Level Output
```
2024-01-01 10:00:00 - perplexity_webui_scraper - DEBUG - Session token provided: ***abc12345
2024-01-01 10:00:00 - perplexity_webui_scraper - DEBUG - Client configured with timeout: 1800s, max files: 30, max file size: 50.0MB
2024-01-01 10:00:01 - perplexity_webui_scraper - DEBUG - Ask parameters - Citation mode: default, Model: Best, Search focus: internet
2024-01-01 10:00:01 - perplexity_webui_scraper - DEBUG - Preparing request data
2024-01-01 10:00:01 - perplexity_webui_scraper - DEBUG - No files to upload
2024-01-01 10:00:01 - perplexity_webui_scraper - DEBUG - HTTP Request: POST https://www.perplexity.ai/rest/sse/perplexity_ask
2024-01-01 10:00:02 - perplexity_webui_scraper - DEBUG - HTTP Response: Status 200
2024-01-01 10:00:02 - perplexity_webui_scraper - DEBUG - Stream established, processing response lines
2024-01-01 10:00:03 - perplexity_webui_scraper - DEBUG - Processing incoming data chunk: ['text', 'final']
2024-01-01 10:00:03 - perplexity_webui_scraper - DEBUG - Found FINAL step, processing answer content
```

## Best Practices

### Production Usage
```python
# Use INFO level for production monitoring
logger = setup_logger(level=logging.INFO, log_file="app.log")
```

### Development/Testing
```python
# Use DEBUG level for development
logger = setup_logger(level=logging.DEBUG, log_file="debug.log")
```

### Error Investigation
```python
# Enable debug when issues occur
from perplexity_webui_scraper import set_debug_level
set_debug_level()  # Switch to DEBUG level
```

### Performance Monitoring
```python
import time
import logging
from perplexity_webui_scraper import setup_logger

logger = setup_logger(level=logging.INFO)

start_time = time.time()
response = client.ask("query").run()
end_time = time.time()

logger.info(f"Query completed in {end_time - start_time:.2f} seconds")
```

## Security Considerations

The logging system automatically masks sensitive information:

- Session tokens are partially hidden (`***abc12345`)
- Authentication headers are marked as `[MASKED]`
- Long request payloads are truncated with `[TRUNCATED]`
- Personal data in queries is not specifically masked

### Custom Masking

```python
# The logger includes helper functions for safe logging
from perplexity_webui_scraper.logger import log_request_details, log_response_details

log_request_details(logger, "POST", url, headers=headers, data=data)
log_response_details(logger, status_code, response_data)
```

## Troubleshooting Common Issues

### No Debug Output
```python
# Make sure DEBUG level is set
from perplexity_webui_scraper import set_debug_level
set_debug_level()
```

### Log File Not Created
```python
# Ensure directory exists
from pathlib import Path
Path("logs").mkdir(exist_ok=True)
logger = setup_logger(log_file="logs/debug.log")
```

### Too Much Output
```python
# Use higher log level
logger = setup_logger(level=logging.WARNING)
```

### Colors Not Working
```python
# Disable colors for file output or unsupported terminals
logger = setup_logger(enable_colors=False)
```

## Example Scripts

Two example scripts are included:

1. **`test.py`** - Enhanced test script with debug demonstrations
2. **`debug_demo.py`** - Advanced debug scenarios and features

Run these to see the debug system in action:

```bash
python test.py           # Basic debug demo
python debug_demo.py     # Advanced debug features
```

## API Reference

### Functions

- `setup_logger(name, level, log_file, enable_colors, format_string)` - Configure a logger
- `get_logger(name)` - Get existing logger or create with defaults
- `set_debug_level(logger_name)` - Switch to DEBUG level
- `log_request_details(logger, method, url, headers, data, params)` - Log HTTP requests safely
- `log_response_details(logger, status_code, response_data)` - Log HTTP responses safely

### Classes

- `ColoredFormatter` - Custom formatter with ANSI color support

This debug system provides comprehensive visibility into the scraper's operation while maintaining security and performance.
