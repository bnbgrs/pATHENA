# Independent Observability privacy handoff

Status: ACTIVE / FINAL VALIDATION CANDIDATE
Generated: 2026-09-09
Branch: `independent/observability-privacy-final-20260909`
Base: `develop/pathena-next@24364b858e15fd9e3b06a9ee2eaf1f580b51364c`

## Mission

Close bounded Beta-24 privacy and console-handler lifecycle gaps in the existing canonical `athena.observability.logging` implementation without entering active Backend, Errors, Spec/Core, UI, Storage or Integrator ownership.

This final branch is rebuilt directly from current Develop and contains only the net reviewed delta. It supersedes the exploratory PR #86 history; no force-push or bot-branch mutation is used.

## Owned product paths

- `src/athena/observability/logging.py`
- `tests/unit/test_logging.py`
- `tests/unit/test_observability_logging_privacy.py`

## Owned documentation paths

- `docs/agent_handoffs/independent_observability.md`
- `docs/agent_handoffs/observability_correlation_gap.md`

No other path is claimed.

## Implemented behavior

### Secret and credential boundary

- redact Authorization and Proxy-Authorization, including Bearer and Basic forms;
- redact Cookie and Set-Cookie text headers;
- redact API-key, password/passwd, secret, credential and token families recursively in structured extras;
- preserve diagnostic token counters such as `token_count`, `max_tokens`, input/output/prompt/completion token counters;
- redact sensitive URL query values while preserving safe route/query context;
- redact OAuth/session-style URL query `code`, `state`, `key`, `nonce` only in URL context so ordinary structured diagnostic fields with those names remain usable;
- remove URL fragments and URL userinfo from technical logs;
- handle escape-aware quoted JSON/JSON-like sensitive values so escaped quotes cannot terminate redaction early;
- redact unquoted multiword secret values through a safe delimiter rather than leaking text after the first whitespace.

### No semantic payload default

Normal technical logging replaces known full-content fields with `[REDACTED_CONTENT]`, including prompt, Knowledge body/content, model output, source chunk/content, chat/document/message content and request/response body families. The same policy applies recursively to structured extras and common text/JSON/URL-query representations while preserving adjacent safe metadata.

This does not claim to implement Protected-Content title policy: that requires real protection context from Security/Core and must not be guessed by the formatter.

### Safe serialization

- sanitize format arguments before `%` interpolation so arbitrary argument `__str__`/`repr` cannot execute before the privacy boundary;
- unknown object values become `<type:ClassName>` rather than arbitrary stringification;
- UUID and datetime retain diagnostic identity/shape;
- bytes expose length only, not contents;
- mappings/sequences are recursively sanitized with cycle and depth bounds;
- non-finite floats become a neutral diagnostic marker;
- exceptions expose class plus traceback basename/line/function only, not exception message or full local filesystem path.

### Structured event compatibility

The existing formatter remains authoritative. It still emits `timestamp`, `level`, `logger`, `message` and producer extras. It additionally emits `component` as a backward-compatible alias of the logger name. Producer-supplied `event`, `job_id` and other real IDs remain preserved after sanitization. The formatter never fabricates placeholder `request_id`, `job_id` or `processing_run_id` values.

### Handler lifecycle

Repeated `configure_logging()` calls keep exactly one ATHENA-owned StreamHandler and rebind it directly to the current `sys.stderr`. This fixes the observed pytest/application-restart failure where the retained handler pointed to a closed capture stream and emitted `ValueError: I/O operation on closed file`. Direct assignment is deliberate because `setStream()` flushes the old stream first and is unsafe when that old stream is already closed.

## Focused regression coverage

Coverage includes:

- machine-readable event fields and `component`;
- configure idempotence and stale/closed stderr rebinding;
- Bearer/Basic authorization and Cookie/Set-Cookie leakage;
- sensitive and semantic URL query handling with safe parameter preservation;
- OAuth URL-only keys versus ordinary structured `state/code/key` fields;
- recursive secret and semantic payload extras;
- JSON-like quoted secrets/content, including escaped quotes;
- unquoted multiword secrets;
- semantic payload text/JSON forms;
- hostile format-argument objects without stringification;
- exception message/path minimization;
- cyclic nested data.

## Canonical Quality evidence from exploratory lineage

- `#4758 @ 60c8a699...`: Spec PASS, Ruff PASS, mypy PASS, Linux Storage PASS, Windows Path PASS, Local Install PASS; full pytest `2 failed, 4825 passed, 3 skipped`. One owned regex bug was fixed later; the other failure was inherited Develop Research-Delta integration loss.
- `#4760 @ 9723a2c...`: product verdict invalidated by external GitHub-runner Chrome APT hash mismatch preventing `libegl1` installation. This infra blocker is tracked in issue #87. Ruff/mypy and independent platform/storage/install lanes passed.
- `#4761 @ 7da5d3b...`: desktop libraries, dependency lock, Spec, Ruff, mypy, Linux Storage, Windows Path and Local Install all passed at last observation; full pytest remained the long-running step.

The final clean branch requires its own exact-head canonical Quality. Do not transfer PASS claims from an ancestor.

## Known inherited Develop blocker

Current Develop `24364b858...` is canonical-pytest red because its explicit-source Delta integration omitted the one-line `ResearchMode.DELTA` allowance in `src/athena/research/repository.py` that exists on exact-green Spec/Core `0c918995...`. This lane reports that integration loss only; it does not patch Research/Core.

## Cross-scope B24 work intentionally not implemented

- API request -> durable Job -> ProcessingRun correlation;
- persistent JSONL `logs_root`, rotation and retention;
- capability-aware Health degradation semantics;
- Protected-Content title/context policy;
- metrics and local crash-reporting runtime composition.

See `observability_correlation_gap.md` for the correlation boundary.

## Bot rules

- Treat this branch/its successor PR as the only current independent Observability candidate.
- Do not copy exploratory PR #86 history into Develop; consume only the clean net delta after exact-head verification.
- Refresh active worker heads before any future mutation.
- Findings in API/Core/Jobs/Security/Storage/Quality remain report-only unless accepted by the owning worker.
- `main` and `bnbgrs/ATHENA` remain untouched.
- No auto-merge.