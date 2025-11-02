"""
FastAPI application exposing the Perplexity WebUI scraper client.

The API wraps the existing synchronous client so callers can submit queries over HTTP.
"""

from collections.abc import Iterator
from os import getenv
from typing import Any

import orjson
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from httpx import HTTPStatusError, RequestError
from pydantic import BaseModel, ConfigDict, Field

from perplexity_webui_scraper import (
    CitationMode,
    ModelType,
    Perplexity,
    SearchFocus,
    SourceFocus,
    TimeRange,
)
from perplexity_webui_scraper.models import ModelBase
from perplexity_webui_scraper.utils import AskResponse, StreamResponse


DEFAULT_SESSION_TOKEN = "pub4ecf63e3fd1ad28de1a9027c01181601"


def _build_model_registry() -> dict[str, type[ModelBase]]:
    registry: dict[str, type[ModelBase]] = {}

    for name, value in vars(ModelType).items():
        if isinstance(value, type) and issubclass(value, ModelBase):
            registry[name.lower()] = value
            identifier = value._get_identifier().lower()
            registry[identifier] = value

    return registry


MODEL_REGISTRY = _build_model_registry()
MODEL_CHOICES = sorted({cls.__name__ for cls in MODEL_REGISTRY.values()})


class AskPayload(BaseModel):
    """Request payload for the /ask endpoints."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(..., description="Question or prompt to send to Perplexity.")
    files: list[str] | None = Field(
        default=None,
        description="Optional file paths accessible to the server that should accompany the query.",
    )
    citation_mode: str = Field(
        default=CitationMode.PERPLEXITY.name,
        description="Citation mode (PERPLEXITY, MARKDOWN, CLEAN).",
    )
    model: str = Field(
        default="claude2",
        description=f"Model to use. Options: {', '.join(MODEL_CHOICES)}.",
    )
    save_to_library: bool = Field(
        default=False,
        description="Whether to save the conversation to the Perplexity library.",
    )
    search_focus: str = Field(
        default=SearchFocus.WEB.name,
        description="Search focus (WEB, WRITING).",
    )
    source_focus: list[str] | str | None = Field(
        default=SourceFocus.WEB.name,
        description="Source focus options (WEB, ACADEMIC, SOCIAL, FINANCE). Accepts string or list.",
    )
    time_range: str | None = Field(
        default=TimeRange.ALL.name,
        description="Time range filter (ALL, TODAY, LAST_WEEK, LAST_MONTH, LAST_YEAR).",
    )
    language: str = Field(default="en-US", description="Language code for the answer.")
    timezone: str | None = Field(default=None, description="Timezone (e.g. America/New_York).")
    coordinates: tuple[float, float] | None = Field(
        default=None,
        description="Latitude and longitude coordinates.",
    )
    session_token: str | None = Field(
        default=None,
        description="Perplexity session token to authenticate the request. Falls back to PERPLEXITY_SESSION_TOKEN env var.",
    )


app = FastAPI(
    title="Perplexity WebUI Scraper API",
    version="0.1.0",
    description="Unofficial API surface for the Perplexity WebUI via the scraper client.",
)


def create_app() -> FastAPI:
    """Return the FastAPI application instance."""

    return app


def _get_session_token(payload: AskPayload) -> str:
    token = payload.session_token or DEFAULT_SESSION_TOKEN
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session token missing. Provide session_token in the request body or set PERPLEXITY_SESSION_TOKEN.",
        )
    return token


def _coerce_enum(value: Any, enum_cls: type[Any], *, allow_none: bool = False):
    if isinstance(value, enum_cls):
        return value

    if value is None:
        if allow_none:
            return None

        if any(member.value is None for member in enum_cls):  # type: ignore[attr-defined]
            return next(member for member in enum_cls if member.value is None)  # type: ignore[attr-defined]

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Value for {enum_cls.__name__} cannot be null.",
        )

    if isinstance(value, str):
        normalised = value.strip().lower()

        for member in enum_cls:  # type: ignore[operator]
            if normalised == member.name.lower():
                return member

            member_value = member.value  # type: ignore[attr-defined]
            if isinstance(member_value, str) and normalised == member_value.lower():
                return member

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid value '{value}' for {enum_cls.__name__}.",
        )

    try:
        return enum_cls(value)  # type: ignore[call-arg]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not convert value '{value}' to {enum_cls.__name__}.",
        ) from exc


def _coerce_model(model_name: str) -> type[ModelBase]:
    normalised = model_name.strip().lower()
    model = MODEL_REGISTRY.get(normalised)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Unknown model '{model_name}'. "
                f"Available options: {', '.join(MODEL_CHOICES)}."
            ),
        )
    return model


def _coerce_source_focus(value: list[str] | str | None) -> SourceFocus | list[SourceFocus]:
    if value is None:
        return SourceFocus.WEB

    if isinstance(value, list):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="source_focus list cannot be empty.",
            )
        return [_coerce_enum(item, SourceFocus) for item in value]

    return _coerce_enum(value, SourceFocus)


def _prepare_parameters(payload: AskPayload) -> dict[str, Any]:
    citation_mode = _coerce_enum(payload.citation_mode, CitationMode)
    search_focus = _coerce_enum(payload.search_focus, SearchFocus)
    time_range = _coerce_enum(payload.time_range, TimeRange, allow_none=True) or TimeRange.ALL
    source_focus = _coerce_source_focus(payload.source_focus)

    return {
        "query": payload.query,
        "files": payload.files,
        "citation_mode": citation_mode,
        "model": _coerce_model(payload.model),
        "save_to_library": payload.save_to_library,
        "search_focus": search_focus,
        "source_focus": source_focus,
        "time_range": time_range,
        "language": payload.language,
        "timezone": payload.timezone,
        "coordinates": payload.coordinates,
    }


def _stream_to_response(stream: Iterator[StreamResponse]) -> Iterator[bytes]:
    for message in stream:
        yield orjson.dumps(message.model_dump()) + b"\n"


def _handle_client_error(exc: HTTPStatusError | RequestError) -> HTTPException:
    if isinstance(exc, HTTPStatusError):
        return HTTPException(
            status_code=exc.response.status_code,
            detail=f"Perplexity returned HTTP {exc.response.status_code}: {exc.response.text}",
        )

    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Request to Perplexity failed: {exc}",
    )


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Simple healthcheck endpoint."""

    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskPayload) -> AskResponse:
    """Submit a question to Perplexity and return the full response once complete."""

    session_token = _get_session_token(payload)
    client = Perplexity(session_token=session_token)
    params = _prepare_parameters(payload)

    try:
        ask_call = client.ask(**params)
        result = ask_call.run()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (HTTPStatusError, RequestError) as exc:
        raise _handle_client_error(exc) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unexpected error while processing query: {exc}",
        ) from exc
    finally:
        client._client.close()


@app.post("/ask/stream")
def ask_stream(payload: AskPayload) -> StreamingResponse:
    """Stream the Perplexity response as newline-delimited JSON."""

    session_token = _get_session_token(payload)
    client = Perplexity(session_token=session_token)
    params = _prepare_parameters(payload)

    try:
        ask_call = client.ask(**params)
        stream = ask_call.stream()
    except ValueError as exc:
        client._client.close()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (HTTPStatusError, RequestError) as exc:
        client._client.close()
        raise _handle_client_error(exc) from exc
    except Exception as exc:
        client._client.close()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unexpected error while starting stream: {exc}",
        ) from exc

    def iterator() -> Iterator[bytes]:
        try:
            yield from _stream_to_response(stream)
        except (HTTPStatusError, RequestError) as exc:
            error_payload = {"error": "perplexity_stream_error", "detail": str(exc)}
            yield orjson.dumps(error_payload) + b"\n"
        finally:
            client._client.close()

    return StreamingResponse(iterator(), media_type="application/jsonl")


__all__ = ["app", "create_app", "AskPayload"]
