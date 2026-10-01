# Observability dynamic-key redaction hardening — 2026-10-02

## Baseline / parallel-work check

- Base: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`.
- No open Observability/Logging PR existed before this branch was created.
- This slice does not touch active Chat, LM Studio, Settings, Storage, Research or Qt-CI files.

## Ausgangslage

`JsonFormatter` recursively sanitized structured **values**, but string keys were emitted unchanged:
- nested `Mapping` keys were copied directly;
- mapping-format argument keys were copied directly;
- top-level `LogRecord.__dict__` extra keys were copied directly and assumed to be strings.

That leaves a privacy escape in a format intended to be privacy-preserving. A dynamic key such as
`password=hunter2`, `prompt=private question`, or a URL containing a secret query parameter can
persist the sensitive text in the JSON field name even when the associated value is safe. A non-string
top-level extra key can also raise from `.startswith()` during formatting.

Beta 24 requires Privacy by Default, no semantic payload in normal logs, secret redaction before
serialization, and sensitive URL query redaction. Those requirements apply to the serialized object,
not only its values.

## Root Cause

The sanitizer treated mapping keys as schema-only metadata and routed only values through the existing
redaction functions. In Python mappings and LogRecord extras can contain runtime/dynamic keys, so this
assumption is not a safe serialization boundary.

## Änderungen

### Product

`src/athena/observability/logging.py`

- added one shared `_safe_mapping_key()` boundary;
- string keys pass through the existing tested `_sanitize_text()` redaction path;
- non-string keys are represented only by safe type names, never arbitrary `str()` / `repr()`;
- nested Mapping sanitization uses the safe serialized key while retaining the original string key as
  the value-classification hint, so existing `password`, `Authorization`, `prompt`, etc. value
  redaction semantics are preserved;
- mapping format arguments use the same boundary;
- top-level LogRecord extras now use the same safe-key path and no longer assume every key supports
  `.startswith()`;
- sanitized keys cannot overwrite formatter-owned fields such as `timestamp` or `message`.

No log schema fields are renamed when their keys contain ordinary technical names.

### Tests

`tests/unit/test_observability_logging_privacy.py`

- proves a secret assignment in a top-level key does not survive serialization;
- proves semantic payload text in a nested key is redacted;
- proves URL query secrets embedded in a key are redacted while safe query context is retained;
- proves a non-string top-level extra key is serialized as a safe type marker instead of crashing.

Existing privacy tests continue to cover normal `Authorization`, prompt, nested secret, URL and opaque
object behavior.

## Validierung

- Manual diff review completed before PR creation.
- The implementation deliberately reuses the already-covered `_sanitize_text()` path rather than
  adding a second redaction grammar.
- Local repository checkout/pytest remains unavailable in this execution runtime because github.com
  DNS resolution fails.
- Exact-head GitHub Quality is required before this slice is Integrator-ready. No CI PASS is claimed
  until observed.

## Konfliktrisiko / Abhängigkeiten

- Low collision risk: this branch modifies only Observability formatter/test/handoff files.
- Do not merge by replacing newer formatter work. If another Observability PR appears, compare exact
  diffs and preserve the single shared sanitizer.
- Persistent JSONL automatically consumes `JsonFormatter`, so no separate JSONL implementation is
  needed; the fix applies to console-structured and persistent JSONL serialization through the shared
  formatter.

## Nächste sinnvolle Schritte

1. Run exact-head canonical Quality.
2. If green, integrate as a bounded privacy hardening slice.
3. After integration, continue Beta 24 correlation/metrics/diagnostics gaps separately; do not broaden
   this privacy fix into an observability redesign.
