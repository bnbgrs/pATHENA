# Backend & Systems Handoff

Generated: 2026-09-10
Branch: `postmerge/backend`

## Current source of truth

- Develop consumed first: `develop/pathena-next@0d3ca68731ded061b0720bd94d649f3dfed59a45`.
- Backend worker head before this handoff refresh: `a5e28d3c9d3f215620fe69a7dfa9e024155037cf`.
- Exact Develop canonical Quality `34486592055@0d3ca68731ded061b0720bd94d649f3dfed59a45 = SUCCESS`.
- Exact Backend canonical Quality remains `34455900467@7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2 = FAILURE`; no worker Quality run was queued or in progress when this refresh began.
- Current Develop handoffs, Alpha/Beta/architecture/runtime/storage contracts and exact-SHA Quality evidence were treated as authoritative over historical queue text.

## Closed verification cluster — Windows packaged runtime contracts

Status: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`.

Develop `0d3ca68731ded061b0720bd94d649f3dfed59a45` adds the existing packaged runtime contract regressions to the canonical Windows path-safety lane. Exact run `34486592055` completed SUCCESS. Within that exact run, Windows steps `Run Windows packaged runtime contract regressions`, `Run Windows Core/API restart smoke`, and `Verify Windows pypdf packaging metadata` all completed SUCCESS. Linux storage regressions, full Python Quality (validator/Ruff/mypy/pytest), and Local install smoke also completed SUCCESS.

This converts the previously inferred Windows evidence for Frozen argv, two-EXE topology and packaged process dispatch into direct canonical Windows evidence. No production packaging/runtime code, assertions, Storage, Recovery or Security guards were weakened.

## Highest current Backend gaps

### BE-046 — Emergency Reserve Windows directory-identity binding

Status: `OPEN / P1 / CURRENTLY REPRODUCED BY SOURCE TRACE`.

Current Develop still binds POSIX reserve creation/release to an opened parent directory FD. The non-POSIX branch still creates via `os.open(self.path, ...)`, validates pathname/file identity after open, and later performs cleanup/release through `self.path.stat()` / `self.path.unlink()`. Therefore directory identity is not bound through the Windows mutation itself. Preserve physical non-sparse allocation and exact release accounting; do not substitute weaker pathname-only checks.

### BE-052 — Preflight DB identity through live writer startup

Status: `OPEN / P1 / CURRENTLY REPRODUCED BY SOURCE TRACE`.

Current Develop `SQLiteDatabase.start()` still calls `inspect_database_read_only(self.path)` and then independently opens the writer with `sqlite3.connect(self.path, ...)`. The identity verified by preflight is not carried into the writable SQLite connection. A second pathname preflight would not close the race; a cross-platform identity-bound writer strategy is still required.

No product mutation was made for BE-046 or BE-052 in this run because the required focused execution path is transiently unavailable: a fresh local checkout again failed with `Could not resolve host: github.com`. No fabricated focused PASS is claimed.

## Previously closed dependency slices

- BE-038 Windows HANDLE-bound durable filesystem publication: `CLOSED_ON_DEVELOP / QUEUE_EVIDENCE_STALE`.
- Schema reinitialization harness regression: `CLOSED_ON_DEVELOP / CANONICAL_GREEN`.
- BE-020 runtime ModelSignature drift guard: `CLOSED_ON_DEVELOP / QUEUE_EVIDENCE_STALE`.
- Windows storage bootstrap reserve-path harness cluster: `CLOSED_ON_DEVELOP / EXACT_LANE_VERIFIED`.

## Current Backend worker red state

The broad historical worker branch remains non-authoritative relative to current Develop. Its last exact canonical run is red and contains worker-only schema-v41 / `research_delta_boundaries` history plus a separate Ruff import-order finding. Do not mechanically repair legacy fixtures to preserve that worker-only lineage.

Integrator has already required that broad Backend/Storage/Migration/Runtime history not be absorbed as a unit. Any surviving worker delta must be re-proven as a small current-Develop gap before mutation or integration.

## Preserved release guards

- No silent Tor-to-Direct fallback.
- Redirect/Auth/HTTPS/response-size boundaries remain fail-closed.
- WAL maintenance safety remains intact.
- pypdf packaging, Frozen argv and two-EXE topology remain guarded and now have exact Windows canonical evidence on `0d3ca68731ded061b0720bd94d649f3dfed59a45`.
- Bounded worker tree and adaptive 2048-context reserve remain guarded.
- Windows lane-lock/path-safety, duplicate-column/Core-startup/storage-bootstrap signatures remain protected and are only OPEN when reproduced on current exact-SHA evidence.
- No Skip/XFail, force push, history rewrite, main mutation, or mutation to `bnbgrs/ATHENA`.

## Integrator prerequisites

- Windows packaged runtime verification cluster: CLOSED on Develop `0d3ca68731ded061b0720bd94d649f3dfed59a45`; canonical Quality `34486592055 = SUCCESS`; no Backend cherry-pick required.
- BE-038 / BE-020 / schema-reinitialization / Windows bootstrap harness: CLOSED on Develop; do not duplicate.
- BE-046 and BE-052 remain OPEN but have no candidate because focused execution is currently infrastructure-blocked.
- Broad Backend worker history: `HOLD / NOT READY`.
- Do not integrate worker-only schema-v41/WAL/Runtime changes without a fresh bounded reconciliation against current Develop and exact focused/canonical evidence.

## Next Backend action

Consume the then-current Develop and Backend exact-SHA results first. If Develop remains green, retry real focused execution and take exactly one bounded current gap, preferring BE-046 before BE-052 unless newer exact-SHA evidence raises a higher-priority Backend/System failure. Do not weaken Storage/Recovery/Security invariants to obtain green tests.
