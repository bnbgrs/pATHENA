# Dynamic structured logging key redaction — current Develop port

## Scope

Current-Develop reconstruction of historical PR #350. The old branch diverged too far to merge safely.

## Fix

- sanitize string mapping keys before they become JSON keys;
- preserve the original raw string as the sensitivity hint so values under keys such as `password=...` and `prompt=...` remain redacted correctly;
- represent non-string keys only by bounded type names;
- make top-level `LogRecord.__dict__` handling safe for non-string injected keys;
- never let dynamic keys bypass URL/query-secret sanitization.

## Regression coverage

`tests/unit/test_observability_logging_privacy.py` now verifies:
- secrets in top-level dynamic keys are absent from encoded logs;
- semantic prompt content in nested keys is redacted;
- URL query secrets embedded in keys are redacted;
- non-string top-level extra keys cannot crash formatting and do not expose `repr` content.

Base: `develop/pathena-next` @ `3357bf1e66d9d60d7b1c9e2d528c36632d89fbc5`.
Historical source: PR #350.
