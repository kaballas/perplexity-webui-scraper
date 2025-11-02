# Standard modules
from collections.abc import Generator
from enum import Enum
from re import Match
from re import compile as re_compile
from typing import Any

# Third-party modules
from pydantic import BaseModel, Field

# Local modules
from .logger import get_logger, log_request_details, log_response_details


class SearchResultItem(BaseModel):
    title: str | None = None
    snippet: str | None = None
    url: str | None = None


class StreamResponse(BaseModel):
    title: str | None = None
    answer: str | None = None
    chunks: list[str] = Field(default_factory=list)
    last_chunk: str | None
    search_results: list[SearchResultItem] = Field(default_factory=list)
    raw_data: dict[str, Any] = Field(default_factory=dict)


class AskResponse(BaseModel):
    title: str | None = None
    answer: str | None = None
    chunks: list[str] = Field(default_factory=list)
    search_results: list[SearchResultItem] = Field(default_factory=list)
    raw_data: dict[str, Any] = Field(default_factory=dict)


class CitationMode(Enum):
    """
    Available citation modes

    Attributes:
        PERPLEXITY: Use default Perplexity citation format (e.g., "`This is a citation[1]`")
        MARKDOWN: Replace citations with real markdown links (e.g., "`This is a citation[1](https://example.com)`")
        CLEAN: Remove all citations (e.g., "`This is a citation`")
    """

    PERPLEXITY = "default"
    MARKDOWN = "markdown"
    CLEAN = "clean"


class SearchFocus(Enum):
    """
    Available search focus

    Attributes:
        WEB: Search the web
        WRITING: Search for writing
    """

    WEB = "internet"
    WRITING = "writing"


class SourceFocus(Enum):
    """
    Available source focus

    Attributes:
        WEB: Search across the entire internet
        ACADEMIC: Search academic papers
        SOCIAL: Discussions and opinions
        FINANCE: Search SEC filings
    """

    WEB = "web"
    ACADEMIC = "scholar"
    SOCIAL = "social"
    FINANCE = "edgar"


class TimeRange(Enum):
    """
    Available time range

    Attributes:
        ALL: Include sources from all time
        TODAY: Include sources from today
        LAST_WEEK: Include sources from the last week
        LAST_MONTH: Include sources from the last month
        LAST_YEAR: Include sources from the last year
    """

    ALL = None
    TODAY = "DAY"
    LAST_WEEK = "WEEK"
    LAST_MONTH = "MONTH"
    LAST_YEAR = "YEAR"


class AskCall:
    def __init__(self, parent, json_data: dict[str, Any]) -> None:
        self._parent = parent
        self._json_data = json_data
        self.logger = get_logger()
        self.logger.debug("AskCall object created")

    def run(self) -> AskResponse:
        """
        Run the ask request and return the response data

        Returns:
            AskResponse object containing the response data.
        """

        self.logger.info("Starting ask request execution (run mode)")
        query = self._json_data["query_str"]
        self.logger.debug(f"Query: {query[:100]}{'...' if len(query) > 100 else ''}")

        self._parent.reset_response_data()

        # Initial request to establish session
        search_url = "https://www.perplexity.ai/search/new"
        params = {"q": query}
        self.logger.debug(f"Making initial request to: {search_url}")
        log_request_details(self.logger, "GET", search_url, params=params)

        initial_response = self._parent._client.get(search_url, params=params)
        log_response_details(self.logger, initial_response.status_code)

        # Main request
        ask_url = "https://www.perplexity.ai/rest/sse/perplexity_ask"
        self.logger.info(f"Starting streaming request to: {ask_url}")
        log_request_details(self.logger, "POST", ask_url, data=self._json_data)

        with self._parent._client.stream(
            "POST", ask_url, json=self._json_data
        ) as response:
            response.raise_for_status()
            log_response_details(self.logger, response.status_code)
            self.logger.debug("Stream established, processing response lines")

            line_count = 0
            for line in response.iter_lines():
                line_count += 1
                if line_count % 10 == 0:  # Log every 10th line to avoid spam
                    self.logger.debug(f"Processed {line_count} lines")

                data = self._parent._extract_json_line(line)

                if data:
                    self._parent._process_data(data)

                    if data.get("final"):
                        self.logger.info("Received final data chunk, request completed")
                        break

            self.logger.info(f"Stream processing completed after {line_count} lines")

        result = AskResponse(
            title=self._parent.title,
            answer=self._parent.answer,
            chunks=list(self._parent.chunks),
            search_results=list(self._parent.search_results),
            raw_data=self._parent.raw_data,
        )

        self.logger.info(f"Ask request completed - Answer: {len(result.answer) if result.answer else 0} chars, " +
                        f"Search results: {len(result.search_results)}, Chunks: {len(result.chunks)}")
        return result

    def stream(self) -> Generator[StreamResponse]:
        """
        Stream response data in real-time

        Yields:
            StreamResponse object containing the streamed data.
        """

        self.logger.info("Starting ask request execution (stream mode)")
        query = self._json_data["query_str"]
        self.logger.debug(f"Query: {query[:100]}{'...' if len(query) > 100 else ''}")

        self._parent.reset_response_data()

        # Initial request to establish session
        search_url = "https://www.perplexity.ai/search/new"
        params = {"q": query}
        self.logger.debug(f"Making initial request to: {search_url}")
        log_request_details(self.logger, "GET", search_url, params=params)

        initial_response = self._parent._client.get(search_url, params=params)
        log_response_details(self.logger, initial_response.status_code)

        # Main streaming request
        ask_url = "https://www.perplexity.ai/rest/sse/perplexity_ask"
        self.logger.info(f"Starting streaming request to: {ask_url}")
        log_request_details(self.logger, "POST", ask_url, data=self._json_data)

        with self._parent._client.stream(
            "POST", ask_url, json=self._json_data
        ) as response:
            response.raise_for_status()
            log_response_details(self.logger, response.status_code)
            self.logger.debug("Stream established, yielding response chunks")

            line_count = 0
            yield_count = 0

            for line in response.iter_lines():
                line_count += 1
                if line_count % 20 == 0:  # Log every 20th line for stream mode
                    self.logger.debug(f"Processed {line_count} lines, yielded {yield_count} responses")

                data = self._parent._extract_json_line(line)

                if data:
                    self._parent._process_data(data)
                    yield_count += 1

                    stream_response = StreamResponse(
                        title=self._parent.title,
                        answer=self._parent.answer,
                        chunks=list(self._parent.chunks),
                        last_chunk=self._parent.last_chunk,
                        search_results=list(self._parent.search_results),
                        raw_data=data,
                    )

                    self.logger.debug(f"Yielding response {yield_count} - Answer: {len(stream_response.answer) if stream_response.answer else 0} chars")
                    yield stream_response

                    if data.get("final"):
                        self.logger.info(f"Stream completed - Final response yielded after {line_count} lines and {yield_count} responses")
                        break

            self.logger.info(f"Stream processing completed: {line_count} lines processed, {yield_count} responses yielded")



def citation_replacer(match: Match[str], citation_mode: CitationMode, search_results: list) -> str:
    logger = get_logger()
    num = match.group(1)
    logger.debug(f"Processing citation [{num}] with mode {citation_mode.value}")

    if not num.isdigit():
        logger.debug(f"Citation number '{num}' is not a digit, returning original")
        return match.group(0)

    idx = int(num) - 1

    if 0 <= idx < len(search_results):
        url = getattr(search_results[idx], "url", "") or ""
        logger.debug(f"Citation [{num}] -> URL: {url[:50]}{'...' if len(url) > 50 else ''}")

        if citation_mode.value == "markdown" and url:
            result = f"[{num}]({url})"
            logger.debug(f"Converted to markdown: {result}")
            return result
        elif citation_mode.value == "clean":
            logger.debug("Removed citation (clean mode)")
            return ""
        else:
            logger.debug("Keeping original citation format")
            return match.group(0)
    else:
        logger.warning(f"Citation [{num}] index {idx} out of range (have {len(search_results)} results)")
        return match.group(0)


def format_citations(citation_mode: CitationMode, text: str, search_results: list) -> str:
    logger = get_logger()

    if not text:
        logger.debug("No text provided for citation formatting")
        return text

    if citation_mode.value == "default":
        logger.debug("Using default citation mode, no formatting needed")
        return text

    logger.debug(f"Formatting citations in text ({len(text)} chars) with mode {citation_mode.value}, {len(search_results)} search results")

    # Count citations before processing
    citation_pattern = re_compile(r"\[(\d{1,2})\](?![\d\w])")
    original_citations = citation_pattern.findall(text)
    logger.debug(f"Found {len(original_citations)} citations: {original_citations}")

    result = citation_pattern.sub(
        lambda match: citation_replacer(match, citation_mode, search_results),
        text
    )

    logger.debug(f"Citation formatting completed - Text length: {len(text)} -> {len(result)}")
    return result
