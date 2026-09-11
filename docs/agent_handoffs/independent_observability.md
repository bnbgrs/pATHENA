# Independent Observability Privacy Handoff

Generated: 2026-09-09
Status: ACTIVE / FOLLOW-UP IMPLEMENTED_PENDING_VERIFY
Branch: `independent/observability-privacy-20260909`
Base: `develop/pathena-next@24364b858e15fd9e3b06a9ee2eaf1f580b51364c`
Draft PR: #86
Superseded predecessor: PR #85 (`independent/coordination-audit-20260909`, closed without merge)

## Purpose

Continue useful pATHENA work without entering active worker ownership. This lane owns only the existing Observability logging privacy/lifecycle boundary and focused regression coverage. It does not introduce a second logging stack and does not mutate Develop, Research, Storage, Backend, Errors, UI or packaging code.

## Collision map refreshed before follow-up mutation

- Develop / Integrator: `24364b858e15fd9e3b06a9ee2eaf1f580b51364c`
- Backend: `844d65a85ecb611d5060bf311c6346c810d2247e`
- Errors: `f861634387527da1894c73b5edf84ccee30c3644`
- Spec/Core: `0c9189954047306cfea947209b51e1a4d0a50aa3`
- UI: `5a168625987fe7096472d81df3261508ec6a1f56`

No active worker handoff claims `src/athena/observability/logging.py`, `tests/unit/test_logging.py`, or the focused Observability privacy test. Refresh heads before any later implementation slice; this snapshot is evidence, not a lock.

## Canonical Quality evidence for first privacy commit

First product commit: `60c8a699ce7a064183e3e0b1f63d554fd9bc62b2`
Canonical Quality Gate: #4758

Results:

- specification validator: PASS
- Ruff: PASS
- mypy: PASS (`418 source files`)
- Linux storage regressions: PASS
- Windows path safety: PASS
- local install smoke: PASS
- full pytest: FAIL (`2 failed, 4825 passed, 3 skipped`)

The two pytest failures have different ownership and were root-caused separately.

### Owned failure — OBS-PRIV-001

`tests/unit/test_observability_logging_privacy.py::test_json_formatter_redacts_secrets_in_message_and_url_query`

The free secret-assignment regex consumed the `&mode=fast` safe query suffix after URL redaction. Root cause: its value class stopped at whitespace/comma/semicolon but not `&`.

Follow-up fix: stop assignment matching at `&` as well, preserving safe URL query context while keeping the secret value redacted.

### Inherited Develop failure — Research Delta integration loss

`tests/unit/test_research_delta.py::test_delta_research_freezes_only_new_explicit_sources`

Develop rejects `ResearchMode.DELTA` in `ResearchRepository.freeze_local_candidates()`. The canonical-green Spec/Core head `0c9189954047306cfea947209b51e1a4d0a50aa3` contains exactly one additional required line in `src/athena/research/repository.py`: `ResearchMode.DELTA,` in the supported-mode set. The Develop integration contains the Delta module, payload validation and test but omitted that repository line.

This is Spec/Core/Integrator ownership. This independent lane does not patch it. The exact diagnosis was posted to the relevant bot/PR conversation.

## OBS-PRIV-001 — structured-log privacy boundary

Status: FOLLOW-UP IMPLEMENTED_PENDING_VERIFY

The existing canonical `athena.observability.logging.JsonFormatter` is retained and hardened in place.

Current bounded behavior:

- redact Authorization/Bearer, API key, password, secret, credential and token families;
- preserve ordinary diagnostic counters such as `token_count`, `max_tokens`, input/output token counts;
- recursively sanitize mappings/sequences with cycle and maximum-depth handling;
- redact sensitive HTTP/HTTPS query values and URL userinfo while preserving safe route/query diagnostics;
- treat OAuth/session-style `code`, `state`, `sig`, `signature`, `session`, `session_id` and `key` query fields as sensitive;
- drop URL fragments unconditionally because they can carry OAuth/session material and are not needed for technical request diagnostics;
- sanitize logging format arguments before interpolation so arbitrary argument `__str__`/`repr` methods are not invoked by `LogRecord.getMessage()`;
- stop blind unknown-object stringification and emit only `<type:ClassName>`;
- retain UUID/datetime structure and byte length without byte contents;
- serialize non-finite floats as bounded markers;
- retain exception type plus file basename/line/function frames while omitting exception messages and full local paths.

Focused privacy coverage now checks:

1. safe URL query context survives secret redaction;
2. OAuth query fields are redacted and fragments removed;
3. nested header/extra redaction and safe token counters;
4. unknown objects are not stringified;
5. message format arguments are sanitized before interpolation;
6. exception messages and local path prefixes are omitted;
7. cyclic nested context is bounded.

## OBS-LIFE-001 — stale console stream lifecycle

Status: IMPLEMENTED_PENDING_VERIFY

### Reproduced defect

Canonical Quality logs repeatedly showed:

`ValueError: I/O operation on closed file`

from the ATHENA-owned `logging.StreamHandler` during later application starts.

Root cause:

1. `AthenaApplication.start()` calls `configure_logging()` repeatedly across application lifecycles.
2. `configure_logging()` intentionally reuses the single ATHENA-owned console handler.
3. Under pytest, the handler can remain bound to an earlier capture `sys.stderr` object after that capture stream is closed.
4. Reconfiguration updated level/formatter but did not bind the reused handler to the current `sys.stderr`.
5. A later log write therefore targeted the closed stream.

### Bounded fix

When the existing ATHENA handler is a `logging.StreamHandler`, rebind its `stream` directly to the current `sys.stderr` before reuse. Direct assignment is intentional: `StreamHandler.setStream()` flushes the previous stream first and is unsafe when that previous stream is already closed.

Regression coverage creates an ATHENA handler on stream A, closes stream A, switches `sys.stderr` to stream B, reconfigures logging, asserts there is still exactly one ATHENA handler, and verifies the next log event is written to stream B without error.

## B24 audit findings intentionally not patched here

These are real gaps but cross active ownership boundaries:

- persistent JSONL logs / `logs_root` / rotation / retention require Settings/Runtime/Integrator composition;
- request correlation exists at the ASGI response boundary but is not propagated into logging/job context; correct implementation crosses API/Core/Jobs;
- Health lifecycle states do not yet match the full B24 `ok/degraded/unavailable/error/recovery_required` capability-aware model; this crosses Core/API lifecycle semantics;
- no dedicated local Metrics or crash-reporting runtime path was found in the current Develop tree.

Do not implement these by inventing formatter dummy values or parallel infrastructure. They should remain explicit Integrator/Core/API/Jobs follow-ups.

## Files owned by this follow-up

- `src/athena/observability/logging.py`
- `tests/unit/test_observability_logging_privacy.py`
- `tests/unit/test_logging.py`
- `docs/agent_handoffs/independent_observability.md`

No Backend, Storage, migration, Research, UI, packaging, Security, `main`, or ATHENA-repository file is modified.

## Verification protocol

1. Run/consume focused logging regressions for the exact follow-up head.
2. Consume canonical Quality for the exact follow-up head.
3. Attribute the known Research Delta baseline failure to Spec/Core/Integrator unless Develop has already incorporated the missing repository line.
4. Fix only failures introduced by the four owned files.
5. Do not claim canonical green while an inherited Develop failure remains.
6. Keep PR #86 draft; no auto-merge, no force update, no mutation of `main`.
