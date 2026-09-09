"""Structured, privacy-preserving technical log events.

This module intentionally contains no file I/O or runtime wiring. It provides
the stable event schema and redaction boundary that persistent JSONL sinks can
reuse without learning domain payload semantics.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Final, TypeAlias
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

REDACTED_SECRET: Final = "[REDACTED]"
REDACTED_CONTENT: Final = "[REDACTED_CONTENT]"
_MAX_REDACTION_DEPTH: Final = 12

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]

_SECRET_NAMES: Final = frozenset(
    {
        "authorization",
        "proxyauthorization",
        "cookie",
        "setcookie",
        "apikey",
        "xapikey",
        "password",
        "passwd",
        "secret",
        "clientsecret",
        "token",
        "accesstoken",
        "refreshtoken",
        "idtoken",
    }
)
_SEMANTIC_PAYLOAD_NAMES: Final = frozenset(
    {
        "body",
        "chattext",
        "content",
        "documentcontent",
        "knowledgebody",
        "messagecontent",
        "modeloutput",
        "outputtext",
        "prompt",
        "sourcechunk",
        "text",
        "title",
    }
)
_URL_NAMES: Final = frozenset(
    {
        "endpoint",
        "requesturl",
        "responseurl",
        "uri",
        "url",
    }
)


class LogLevel(StrEnum):
    """Normative technical log levels from Beta chapter 24."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def _normalized_name(name: str) -> str:
    return "".join(character for character in name.casefold() if character.isalnum())


def _is_secret_name(name: str) -> bool:
    normalized = _normalized_name(name)
    return normalized in _SECRET_NAMES or normalized.endswith("password") or normalized.endswith(
        "secret"
    )


def _is_semantic_payload_name(name: str) -> bool:
    return _normalized_name(name) in _SEMANTIC_PAYLOAD_NAMES


def _is_url_name(name: str) -> bool:
    return _normalized_name(name) in _URL_NAMES


def sanitize_url(value: str) -> str:
    """Redact sensitive query-parameter values from an HTTP(S) URL."""

    split = urlsplit(value)
    if split.scheme.casefold() not in {"http", "https"} or not split.netloc:
        return value
    if not split.query:
        return value

    redacted_query = [
        (key, REDACTED_SECRET if _is_secret_name(key) else query_value)
        for key, query_value in parse_qsl(split.query, keep_blank_values=True)
    ]
    return urlunsplit(
        (
            split.scheme,
            split.netloc,
            split.path,
            urlencode(redacted_query, doseq=True),
            split.fragment,
        )
    )


def redact_value(value: object, *, field_name: str | None = None) -> JsonValue:
    """Return a JSON-safe value after fail-closed privacy redaction.

    Known secret-bearing fields are always replaced. Known semantic payload
    fields are replaced rather than copied into technical logs. Exceptions
    expose only their class name; their message/repr is deliberately ignored.
    Unsupported object types raise ``TypeError`` rather than falling back to a
    potentially sensitive ``repr``.
    """

    return _redact_value(value, field_name=field_name, depth=0)


def _redact_value(
    value: object,
    *,
    field_name: str | None,
    depth: int,
) -> JsonValue:
    if field_name is not None:
        if _is_secret_name(field_name):
            return REDACTED_SECRET
        if _is_semantic_payload_name(field_name):
            return REDACTED_CONTENT

    if depth > _MAX_REDACTION_DEPTH:
        return REDACTED_CONTENT

    if isinstance(value, BaseException):
        return {"exception_class": type(value).__name__}

    if value is None or isinstance(value, (str, bool, int)):
        if isinstance(value, str) and (
            (field_name is not None and _is_url_name(field_name))
            or value.casefold().startswith(("http://", "https://"))
        ):
            return sanitize_url(value)
        return value

    if isinstance(value, float):
        if not (float("-inf") < value < float("inf")):
            raise ValueError("Observability values must be finite JSON numbers.")
        return value

    if isinstance(value, Mapping):
        result: dict[str, JsonValue] = {}
        for key, nested_value in value.items():
            if not isinstance(key, str):
                raise TypeError("Observability mapping keys must be strings.")
            result[key] = _redact_value(
                nested_value,
                field_name=key,
                depth=depth + 1,
            )
        return result

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [
            _redact_value(item, field_name=None, depth=depth + 1)
            for item in value
        ]

    raise TypeError(
        "Unsupported observability value type; explicit safe conversion is required: "
        f"{type(value).__name__}"
    )


@dataclass(frozen=True, slots=True)
class LogEvent:
    """Stable v1 structured technical-log event."""

    timestamp: str
    level: LogLevel
    component: str
    event: str
    request_id: str
    job_id: str | None = None
    processing_run_id: str | None = None
    error_code: str | None = None
    duration_ms: int | None = None
    attributes: Mapping[str, object] = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        for name in ("timestamp", "component", "event", "request_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string.")
        if not isinstance(self.level, LogLevel):
            raise TypeError("level must be a LogLevel.")
        for name in ("job_id", "processing_run_id", "error_code"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string.")
        if self.duration_ms is not None:
            if isinstance(self.duration_ms, bool) or not isinstance(self.duration_ms, int):
                raise TypeError("duration_ms must be None or an integer.")
            if self.duration_ms < 0:
                raise ValueError("duration_ms must not be negative.")
        if not isinstance(self.attributes, Mapping):
            raise TypeError("attributes must be a mapping.")

    def to_dict(self) -> dict[str, JsonValue]:
        """Return the stable v1 event shape with sanitized attributes."""

        attributes = redact_value(self.attributes, field_name="attributes")
        if not isinstance(attributes, dict):
            raise AssertionError("attributes redaction must preserve mapping shape")
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "component": self.component,
            "event": self.event,
            "request_id": self.request_id,
            "job_id": self.job_id,
            "processing_run_id": self.processing_run_id,
            "error_code": self.error_code,
            "duration_ms": self.duration_ms,
            "attributes": attributes,
        }


def serialize_event(event: LogEvent) -> str:
    """Serialize one event as exactly one deterministic JSON Lines record."""

    if not isinstance(event, LogEvent):
        raise TypeError("event must be a LogEvent.")
    return (
        json.dumps(
            event.to_dict(),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    )
