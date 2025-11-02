# Standard modules
from importlib.metadata import version

# Local modules
from .core import Perplexity
from .logger import setup_logger, get_logger, set_debug_level
from .models import ModelType
from .utils import (
    CitationMode,
    SearchFocus,
    SourceFocus,
    TimeRange,
)


__all__ = [
    "Perplexity",
    "ModelType",
    "CitationMode",
    "SearchFocus",
    "SourceFocus",
    "TimeRange",
    "setup_logger",
    "get_logger",
    "set_debug_level",
]
__version__ = version("perplexity-webui-scraper")
