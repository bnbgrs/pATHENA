"""Structured console logging for ATHENA."""

from __future__ import annotations

import json
import logging
import math
import re
import sys
import traceback
from collections.abc import Mapping
from datetime import datetime, timezone
from types import TracebackType
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from uuid import UUID

_HANDLER_MARKER = "_athena_console_handler"
_REDACTED = "[REDACTED]"
_REDACTED_CONTENT = "[REDACTED_CONTENT]"
_MAX_SANITIZE_DEPTH = 8

_SENSITIVE_KEY_NAMES = frozenset(
    {
        "authorization",
        "proxyauthorization",
        "cookie",
        "setcookie",
        "apikey",
        "password",
        "passwd",
        "secret",
        "clientsecret",
        "token",
        "accesstoken",
        "refreshtoken",
        "credential",
        "credentials",
        "sig",
        "signature",
        "session",
        "sessionid",
    }
)
_SENSITIVE_URL_QUERY_NAMES = frozenset({"code", "state", "key", "nonce"})
_SEMANTIC_PAYLOAD_KEY_NAMES = frozenset(
    {
        "knowledgebody",
        "prompt",
        "modeloutput",
        "sourcechunk",
        "chattext",
        "documentcontent",
        "messagecontent",
        "outputtext",
        "knowledgecontent",
        "sourcecontent",
        "requestbody",
        "responsebody",
        "content",
        "text",
        "body",
    }
)
_SENSITIVE_KEY_SUFFIXES = (
    "password",
    "passwd",
    "secret",
    "token",
    "apikey",
    "credential",
)
_NON_SECRET_TOKEN_KEYS = frozenset(
    {
        "tokencount",
        "maxtokens",
        "inputtokens",
        "outputtokens",
        "prompttokens",
        "completiontokens",
    }
)
_TEXT_SECRET_KEY_PATTERN = (
    r"api[-_ ]?key|password|passwd|client[-_ ]?secret|"
    r"access[-_ ]?token|refresh[-_ ]?token|token|secret|credential(?:s)?|"
    r"cookie|set[-_ ]?cookie"
)
_SEMANTIC_PAYLOAD_TEXT_PATTERN = (
    r"knowledge[-_ ]?body|prompt|model[-_ ]?output|source[-_ ]?chunk|"
    r"chat[-_ ]?text|document[-_ ]?content|message[-_ ]?content|"
    r"output[-_ ]?text|knowledge[-_ ]?content|source[-_ ]?content|"
    r"request[-_ ]?body|response[-_ ]?body|content|text|body"
)

_URL_RE = re.compile(r"https?://[^\s<>\"']+", flags=re.IGNORECASE)
_BEARER_RE = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]+", flags=re.IGNORECASE)
_AUTHORIZATION_HEADER_RE = re.compile(
    r"\b(?P<key>authorization|proxy[-_ ]?authorization)"
    r"(?P<sep>\s*[:=]\s*)"
    r"(?:(?P<scheme>basic|bearer)(?P<scheme_space>\s+))?"
    r"(?P<value>[^\s,;]+)",
    flags=re.IGNORECASE,
)
_COOKIE_HEADER_RE = re.compile(
    r"\b(?P<key>set-cookie|cookie)(?P<sep>\s*:\s*)(?P<value>[^\r\n]+)",
    flags=re.IGNORECASE,
)
_JSON_SECRET_DOUBLE_ASSIGNMENT_RE = re.compile(
    rf"(?P<prefix>[\"'](?:{_TEXT_SECRET_KEY_PATTERN})[\"']\s*:\s*)"
    r'(?P<quote>")(?P<value>(?:\\.|[^"\\])*)(?P=quote)',
    flags=re.IGNORECASE,
)
_JSON_SECRET_SINGLE_ASSIGNMENT_RE = re.compile(
    rf"(?P<prefix>[\"'](?:{_TEXT_SECRET_KEY_PATTERN})[\"']\s*:\s*)"
    r"(?P<quote>')(?P<value>(?:\\.|[^'\\])*)(?P=quote)",
    flags=re.IGNORECASE,
)
_JSON_SEMANTIC_DOUBLE_ASSIGNMENT_RE = re.compile(
    rf"(?P<prefix>[\"'](?:{_SEMANTIC_PAYLOAD_TEXT_PATTERN})[\"']\s*:\s*)"
    r'(?P<quote>")(?P<value>(?:\\.|[^"\\])*)(?P=quote)',
    flags=re.IGNORECASE,
)
_JSON_SEMANTIC_SINGLE_ASSIGNMENT_RE = re.compile(
    rf"(?P<prefix>[\"'](?:{_SEMANTIC_PAYLOAD_TEXT_PATTERN})[\"']\s*:\s*)"
    r"(?P<quote>')(?P<value>(?:\\.|[^'\\])*)(?P=quote)",
    flags=re.IGNORECASE,
)
_SECRET_ASSIGNMENT_RE = re.compile(
    rf"(?P<key>{_TEXT_SECRET_KEY_PATTERN})"
    r"(?P<sep>\s*[:=]\s*)"
    r"(?P<value>[^\r\n,;&]*)",
    flags=re.IGNORECASE,
)
_SEMANTIC_ASSIGNMENT_RE = re.compile(
    rf"(?<![?&])\b(?P<key>{_SEMANTIC_PAYLOAD_TEXT_PATTERN})"
    r"(?P<sep>\s*[:=]\s*)"
    r"(?P<value>[^\r\n]*)",
    flags=re.IGNORECASE,
)


def _normalized_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", key.casefold())


def _is_sensitive_key(key: str) -> bool:
    normalized = _normalized_key(key)
    if normalized in _NON_SECRET_TOKEN_KEYS:
        return False
    if normalized in _SENSITIVE_KEY_NAMES:
        return True
    return normalized.endswith(_SENSITIVE_KEY_SUFFIXES)


def _is_semantic_payload_key(key: str) -> bool:
    return _normalized_key(key) in _SEMANTIC_PAYLOAD_KEY_NAMES


def _is_sensitive_url_query_key(key: str) -> bool:
    normalized = _normalized_key(key)
    return (
        _is_sensitive_key(key)
        or _is_semantic_payload_key(key)
        or normalized in _SENSITIVE_URL_QUERY_NAMES
    )


def _redact_url(raw_url: str) -> str:
    try:
        parts = urlsplit(raw_url)
    except ValueError:
        return _REDACTED

    host = parts.hostname
    if host is None:
        return _REDACTED

    try:
        port = parts.port
    except ValueError:
        return _REDACTED

    host_display = f"[{host}]" if ":" in host and not host.startswith("[") else host
    host_port = f"{host_display}:{port}" if port is not None else host_display
    netloc = f"{_REDACTED}@{host_port}" if parts.username is not None else host_port

    query_pairs = parse_qsl(parts.query, keep_blank_values=True)
    redacted_query = urlencode(
        [
            (
                key,
                _REDACTED_CONTENT
                if _is_semantic_payload_key(key)
                else _REDACTED
                if _is_sensitive_url_query_key(key)
                else value,
            )
            for key, value in query_pairs
        ],
        doseq=True,
    )
    # URL fragments can carry OAuth/session material and are not required for
    # technical request diagnostics. Drop them unconditionally.
    return urlunsplit((parts.scheme, netloc, parts.path, redacted_query, ""))


def _redact_quoted_assignments(
    text: str,
    *,
    patterns: tuple[re.Pattern[str], ...],
    marker: str,
) -> str:
    for pattern in patterns:
        text = pattern.sub(
            lambda match: (
                f"{match.group('prefix')}{match.group('quote')}"
                f"{marker}{match.group('quote')}"
            ),
            text,
        )
    return text


def _sanitize_text(value: str) -> str:
    text = _URL_RE.sub(lambda match: _redact_url(match.group(0)), value)

    def replace_authorization(match: re.Match[str]) -> str:
        scheme = match.group("scheme")
        scheme_prefix = f"{scheme} " if scheme is not None else ""
        return f"{match.group('key')}{match.group('sep')}{scheme_prefix}{_REDACTED}"

    text = _AUTHORIZATION_HEADER_RE.sub(replace_authorization, text)
    text = _COOKIE_HEADER_RE.sub(
        lambda match: f"{match.group('key')}{match.group('sep')}{_REDACTED}",
        text,
    )
    text = _BEARER_RE.sub(f"Bearer {_REDACTED}", text)
    text = _redact_quoted_assignments(
        text,
        patterns=(
            _JSON_SECRET_DOUBLE_ASSIGNMENT_RE,
            _JSON_SECRET_SINGLE_ASSIGNMENT_RE,
        ),
        marker=_REDACTED,
    )
    text = _redact_quoted_assignments(
        text,
        patterns=(
            _JSON_SEMANTIC_DOUBLE_ASSIGNMENT_RE,
            _JSON_SEMANTIC_SINGLE_ASSIGNMENT_RE,
        ),
        marker=_REDACTED_CONTENT,
    )

    def replace_assignment(match: re.Match[str]) -> str:
        return f"{match.group('key')}{match.group('sep')}{_REDACTED}"

    text = _SECRET_ASSIGNMENT_RE.sub(replace_assignment, text)
    return _SEMANTIC_ASSIGNMENT_RE.sub(
        lambda match: f"{match.group('key')}{match.group('sep')}{_REDACTED_CONTENT}",
        text,
    )


def _safe_type_name(value: object) -> str:
    return f"<type:{type(value).__name__}>"


def _sanitize_value(
    value: object,
    *,
    key_hint: str | None = None,
    depth: int = 0,
    seen: set[int] | None = None,
) -> object:
    if key_hint is not None and _is_sensitive_key(key_hint):
        return _REDACTED
    if key_hint is not None and _is_semantic_payload_key(key_hint):
        return _REDACTED_CONTENT
    if depth >= _MAX_SANITIZE_DEPTH:
        return "<max-depth>"

    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else "<non-finite-float>"
    if isinstance(value, str):
        return _sanitize_text(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, bytes):
        return f"<bytes:{len(value)}>"

    if seen is None:
        seen = set()

    if isinstance(value, Mapping):
        identity = id(value)
        if identity in seen:
            return "<cycle>"
        seen.add(identity)
        try:
            sanitized_mapping: dict[str, object] = {}
            for raw_key, raw_value in value.items():
                key = raw_key if isinstance(raw_key, str) else _safe_type_name(raw_key)
                sanitized_mapping[key] = _sanitize_value(
                    raw_value,
                    key_hint=key,
                    depth=depth + 1,
                    seen=seen,
                )
            return sanitized_mapping
        finally:
            seen.remove(identity)

    if isinstance(value, (list, tuple)):
        identity = id(value)
        if identity in seen:
            return "<cycle>"
        seen.add(identity)
        try:
            return [
                _sanitize_value(item, depth=depth + 1, seen=seen)
                for item in value
            ]
        finally:
            seen.remove(identity)

    return _safe_type_name(value)


def _sanitize_format_args(args: object) -> object:
    if isinstance(args, Mapping):
        sanitized_mapping: dict[str, object] = {}
        for raw_key, raw_value in args.items():
            key = raw_key if isinstance(raw_key, str) else _safe_type_name(raw_key)
            sanitized_mapping[key] = _sanitize_value(raw_value, key_hint=key)
        return sanitized_mapping
    if isinstance(args, tuple):
        return tuple(_sanitize_value(item) for item in args)
    return _sanitize_value(args)


def _safe_log_message(record: logging.LogRecord) -> str:
    if isinstance(record.msg, str):
        template = record.msg
    else:
        sanitized_message = _sanitize_value(record.msg)
        if isinstance(sanitized_message, str):
            return sanitized_message
        return json.dumps(
            sanitized_message,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )

    if not record.args:
        return _sanitize_text(template)

    safe_args = _sanitize_format_args(record.args)
    try:
        rendered = template % safe_args
    except (KeyError, TypeError, ValueError):
        # Malformed format records still produce a useful event without
        # falling back to raw argument repr/str behavior.
        rendered = f"{template} [formatting-error]"
    return _sanitize_text(rendered)


def _safe_frame_filename(filename: str) -> str:
    return filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]


def _safe_exception(
    exc_type: type[BaseException],
    exc_tb: TracebackType | None,
) -> dict[str, object]:
    payload: dict[str, object] = {"type": exc_type.__name__}
    if exc_tb is not None:
        payload["frames"] = [
            {
                "file": _safe_frame_filename(frame.filename),
                "line": frame.lineno,
                "function": frame.name,
            }
            for frame in traceback.extract_tb(exc_tb)
        ]
    return payload


class JsonFormatter(logging.Formatter):
    """Small deterministic JSON formatter for Core diagnostic events."""

    _standard_fields = frozenset(
        {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "taskName",
        }
    )

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "component": record.name,
            "message": _safe_log_message(record),
        }

        for key, value in record.__dict__.items():
            if (
                key not in self._standard_fields
                and not key.startswith("_")
                and key not in payload
            ):
                payload[key] = _sanitize_value(value, key_hint=key)

        if record.exc_info:
            exc_type, _exc_value, exc_tb = record.exc_info
            if exc_type is not None:
                payload["exception"] = _safe_exception(exc_type, exc_tb)

        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )


def _validated_log_level(level: object) -> int:
    if isinstance(level, bool):
        raise ValueError("ATHENA logging level must not be a boolean.")
    if isinstance(level, str):
        normalized = level.strip().upper()
        if not normalized:
            raise ValueError("ATHENA logging level must not be empty.")
        numeric = logging.getLevelNamesMapping().get(normalized)
        if not isinstance(numeric, int):
            raise ValueError(f"Unknown ATHENA logging level {level!r}.")
        return numeric
    if isinstance(level, int):
        if level < 0:
            raise ValueError("ATHENA logging level must be non-negative.")
        return level
    raise ValueError("ATHENA logging level must be an integer or level name.")


def configure_logging(level: int | str = logging.INFO) -> None:
    """Configure exactly one ATHENA-owned console handler.

    Repeated calls update the handler and root log level without creating
    duplicate log lines. Rebind the owned console handler to the current
    ``sys.stderr`` so application restarts do not retain a closed capture
    stream from an earlier runtime/test phase.
    """
    numeric_level = _validated_log_level(level)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    athena_handlers = [
        handler
        for handler in root_logger.handlers
        if getattr(handler, _HANDLER_MARKER, False)
    ]

    if athena_handlers:
        handler = athena_handlers[0]
        if isinstance(handler, logging.StreamHandler):
            # Assign directly rather than setStream(): setStream() flushes the
            # old stream first, which is unsafe when it has already closed.
            handler.stream = sys.stderr
        handler.setLevel(numeric_level)
        handler.setFormatter(JsonFormatter())

        for duplicate in athena_handlers[1:]:
            root_logger.removeHandler(duplicate)
            duplicate.close()
        return

    handler = logging.StreamHandler()
    setattr(handler, _HANDLER_MARKER, True)
    handler.setLevel(numeric_level)
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)
