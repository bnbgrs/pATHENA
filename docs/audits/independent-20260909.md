# Independent audit — Beta 24 Logging, Monitoring, Observability

Observed: 2026-09-09T16:52:12+02:00
Shared baseline audited: `develop/pathena-next@c830b96a12d25914c52a0abc7749a6724b19cfae`
Independent implementation branch: `independent/coordination-audit-20260909`
Independent implementation commit at start of this note: `8904ed7e867e1671b80520780dd17e2ade21e0b7`
Scope owner: independent collision-safe lane / PR #85

## Purpose

Revalidate Beta chapter 24 against the current shared integration baseline without treating the stale August feature-gap backlog as authoritative and without entering active Backend, Errors, Spec/Core, UI or Integrator ownership.

This audit distinguishes:

- **BASELINE EVIDENCE** — observed on the exact shared baseline;
- **INDEPENDENT FOUNDATION** — implemented only on this isolated branch;
- **OPEN** — not closed by this lane;
- **DEFER / OWNER** — requires composition in an active worker's subsystem and is therefore not patched here.

No claim in this document promotes the full B24 chapter to complete.

## Collision check before implementation

Observed active worker heads immediately before the slice:

- `postmerge/backend@b2a2a20873390098f98a9125222ae5594a9d6cc9` — schema v41 / Storage fixtures / protected-source verification;
- `postmerge/errors@1f9c41d7dd88945876ab0eb2a9893a05a3a1117e` — protected-source verification/error classification;
- `postmerge/spec-core@a9b1cb8b3354c9afdc206fbf435af0d1bf5d451f` — Research Delta durable enqueue validation;
- `postmerge/ui@90a51e111851f80c5e2388c11c4026c6ec62fa09` — 44 px send target / QSS box-model contract;
- `develop/pathena-next@c830b96a12d25914c52a0abc7749a6724b19cfae` — shared Integrator / Windows two-EXE packaging evidence.

The independent implementation therefore created only:

- `src/athena/observability/__init__.py`
- `src/athena/observability/structured_log.py`
- `tests/unit/test_structured_log.py`

No pre-existing runtime, storage, UI, Core, Jobs, Error-ledger or packaging file was edited.

## Current-baseline trace

Read-only discovery on the exact shared baseline found no dedicated `src/athena/observability`, `logging`, `logger`, `jsonl` or `telemetry` path in the recursive tree. The main CLI launcher uses direct stdout/stderr diagnostics and does not import Python logging or a structured-log sink. Repository code-search results for `logging` and `redact` were empty; because code-search indexing can lag, those empty results are supporting evidence only, not the sole basis of this audit.

The Beta 24 SSOT requires, among other things:

1. structured technical events with at least `timestamp`, `level`, `component`, `event`, `request_id` and optional `job_id`, `processing_run_id`, `error_code`, `duration_ms`;
2. persistent technical logs as JSON Lines;
3. consistent DEBUG/INFO/WARNING/ERROR/CRITICAL levels;
4. privacy-by-default: no normal full Knowledge bodies, prompts, model outputs or source chunks;
5. redaction of secrets, authorization/cookie/API-key-like headers and sensitive URL query parameters;
6. no blind exception `repr()` when request/payload data could leak;
7. bounded rotation/retention in a local `logs_root`;
8. correlation through request/job/processing-run IDs;
9. technical metrics and a capability-aware health model;
10. local crash reporting without automatic upload;
11. schema, secret-redaction, protected-redaction, rotation, correlation, health, crash-bundle and retention tests.

## Requirement / evidence matrix

| B24 area | Shared baseline | Independent foundation | Status after this slice | Next owner/action |
| --- | --- | --- | --- | --- |
| Structured event schema | No dedicated shared observability schema identified | `LogEvent` supplies a fixed v1 shape including all B24 minimum/correlation fields plus sanitized `attributes` | **FOUNDATION IMPLEMENTED** | Integrator/Core may later wire producers after ownership is free |
| Log levels | No central B24 enum identified | `LogLevel` defines exactly DEBUG/INFO/WARNING/ERROR/CRITICAL | **FOUNDATION IMPLEMENTED** | Reuse; do not create per-subsystem duplicate enums |
| JSON Lines | No persistent shared sink identified | `serialize_event()` emits one deterministic JSON object plus exactly one newline | **PARTIAL** | File sink/rotation remains OPEN |
| Secret/header redaction | No central redaction boundary identified | Recursive field-name sanitizer covers Authorization, Proxy-Authorization, Cookie/Set-Cookie, API-key variants, password/secret/token families | **FOUNDATION IMPLEMENTED** | Runtime callers must pass structured attributes through this boundary |
| URL query redaction | No central sanitizer identified | HTTP(S) URL sanitizer redacts sensitive query parameter values while preserving non-sensitive context | **FOUNDATION IMPLEMENTED** | Expand only from concrete SSOT/provider evidence, not ad-hoc payload logging |
| Semantic payload default | CLI/runtime diagnostics are not a central structured-log contract | Known prompt/content/Knowledge/source/model-output/title fields are replaced with `[REDACTED_CONTENT]` | **FOUNDATION IMPLEMENTED / CONSERVATIVE** | Protected-content integration test still required |
| Exception objects | No central serializer identified | Exceptions serialize class only; message/repr is never copied implicitly | **FOUNDATION IMPLEMENTED** | A later sanitized-stack facility should be separate and explicit |
| Unsupported object safety | No central contract identified | Serializer fails closed with `TypeError`; it never falls back to arbitrary `repr()` | **FOUNDATION IMPLEMENTED** | Preserve this invariant in future sinks |
| Rotation / retention / `logs_root` | Not established by this audit | Deliberately not implemented | **OPEN** | Independent candidate only after checking Storage/Integrator ownership; otherwise Backend/Integrator handoff |
| Request ID assignment | Existing APIs may have domain IDs, but no B24-wide assignment trace completed | Schema accepts `request_id` | **OPEN / DEFER CORE** | Core/API owner must define assignment/propagation |
| Job / ProcessingRun propagation | Existing domain objects exist; cross-layer B24 correlation not traced here | Schema accepts IDs | **OPEN / DEFER CORE/JOBS** | Owning workers should add correlation tests when free |
| Metrics | Not comprehensively audited | Not implemented | **OPEN** | Separate future audit; avoid mixing with this logging slice |
| Health model | Not comprehensively audited because Core is active | Not implemented | **DEFER CORE** | Audit after current Spec/Core lane releases ownership |
| Crash reporting | No B24 implementation established by this audit | Not implemented | **OPEN** | Candidate future independent slice if path remains unowned |
| External telemetry | No dependency introduced | None; utility is local and pure | **PRESERVED** | No automatic upload may be added |
| Schema test | No dedicated B24 schema test identified | Added fixed-key/order/value test | **IMPLEMENTED ON BRANCH** | CI must pass before claiming verification |
| Secret leak test | No dedicated central test identified | Added nested secret/header/query/exception leak regressions | **IMPLEMENTED ON BRANCH** | CI must pass before claiming verification |
| Protected-content integration test | Not traced | Unit-level semantic-field redaction only | **OPEN** | Requires domain integration; do not fake with unit-only claim |
| Rotation test | Not established | None | **OPEN** | Requires sink/retention implementation first |
| Correlation test | Not established | Schema-only assertions | **OPEN** | Requires API→Job→ProcessingRun composition |

## Design invariants introduced by the foundation

1. **No implicit `repr()`.** Unknown objects are rejected rather than stringified.
2. **Exceptions are data-minimized.** The generic path exposes exception class only.
3. **Semantic payload fields are fail-closed.** Known full-content field names are redacted, not merely secret-scanned.
4. **Nested structures are sanitized recursively.** Redaction is not limited to top-level mappings.
5. **Redaction recursion is bounded.** Deep structures stop rather than creating unbounded diagnostic work.
6. **Non-finite floats are rejected.** JSON output cannot silently emit NaN/Infinity extensions.
7. **No I/O side effects.** This foundation does not create directories/files, alter runtime startup, spawn threads, configure global loggers or touch retention.
8. **No external telemetry.** The implementation has no network dependency or upload behavior.

## Verification state

- Source files were syntax-compiled locally before commit.
- Repository Quality Gate run `34366372995` / run number `4745` was triggered for commit `8904ed7e867e1671b80520780dd17e2ade21e0b7`.
- At 2026-09-09T16:52:12+02:00 the workflow had not produced jobs yet; therefore **NO CI PASS IS CLAIMED** in this note.
- Full B24 is **NOT COMPLETE**. The current delta is a reusable foundation plus regressions only.

## Next safe sequence

1. Wait only in the logical sense of verification ordering; continue useful audit work while CI runs. Do not merge this draft PR.
2. If Quality Gate reports a failure attributable to this branch, repair only the smallest root cause in the new observability files/tests.
3. Re-check active worker heads before taking another code slice.
4. Preferred next independent candidate: a bounded local JSONL file sink with explicit size/age retention **only if** it can be implemented without entering Backend Storage, application composition, Error handling, or Integrator packaging paths.
5. If sink ownership is ambiguous, do not implement it; instead audit local crash-reporting or B24 metric/health coverage and hand off overlaps to the owning worker.

## Promotion warning

PR #85 remains a draft and must not be merged merely because the new utility tests pass. Promotion requires exact-head CI evidence, a fresh collision comparison against `develop/pathena-next`, and explicit review that the conservative field-name redaction does not conflict with a newer observability contract introduced by another worker.