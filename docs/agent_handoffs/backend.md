# Backend & Systems Handoff

Generated: 2026-09-10
Branch: `postmerge/backend`

## Current source of truth

- Develop consumed first: `develop/pathena-next@7fa2108d820cfc5b48a9f92d42ffa61697b74818`.
- Backend worker head before this handoff refresh: `baae5dd42195eea1e2a7320d1be813431a3beecf`.
- Exact Develop canonical Quality `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`.
- The exact Develop run completed the canonical Windows durable-filesystem lane together with Linux storage, Python Quality and local-install coverage successfully.
- No canonical Quality run was queued or in progress on the current Backend worker head when this refresh began.
- Current Develop handoffs, Alpha/Beta/architecture/runtime/storage contracts and exact-SHA Quality evidence remain authoritative over historical queue text.

## Closed root-cause cluster — native Windows durable-FS lane / POSIX harness isolation

Status: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`.

Develop `effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36` had introduced the complete durable-filesystem test module into the native Windows storage lane. Canonical run `34516879382` failed only because three explicitly POSIX durable-FS tests forced `_is_windows=False` while still executing on a Windows runner, then reached POSIX directory-FD semantics that Windows cannot provide. The real Windows durable-FS tests themselves passed. Root cause was therefore lane/harness drift, not product Storage behavior.

The bounded Backend candidate `baae5dd42195eea1e2a7320d1be813431a3beecf` isolated the POSIX-only durable-FS cases from the Windows lane without deleting tests, adding Skip/XFail, weakening assertions, or changing Storage/Recovery product code. The equivalent fix is now integrated on Develop as `7fa2108d820cfc5b48a9f92d42ffa61697b74818` (`ci(windows): isolate POSIX durable fs contracts`). Exact canonical Quality run `34522965434` completed `SUCCESS`.

The POSIX durable-FS contracts remain exercised by the Linux lane; native Windows continues to exercise its platform-appropriate durable-filesystem and path-safety contracts. No Backend cherry-pick is required for this cluster.

## Previously closed verification clusters

### Windows Core/API server lifecycle

Status: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`.

Develop `f29abc4341895f8ecd28ebeb0baa2e80b030fdf7` added the already-existing `tests/unit/test_api_server_lifecycle_boundaries.py` to the canonical Windows ownership/lifecycle lane. Exact run `34510755656` completed SUCCESS.

### Windows Core/API ownership lifecycle

Status: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`.

Develop `e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58` added the existing Core/API process ownership/lifecycle regression set to the canonical Windows path-safety lane. Exact run `34504620300` completed SUCCESS.

### Windows adaptive chat reserve

Status: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`.

Develop `3330a0092eaddf58fd3a4fdcb7128f77f01b0301` added the existing adaptive chat reserve contract to the canonical Windows path-safety lane. Exact run `34492275924` completed SUCCESS.

### Windows packaged runtime contracts

Status: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`.

Develop `0d3ca68731ded061b0720bd94d649f3dfed59a45` added the existing packaged runtime contract regressions to the canonical Windows path-safety lane. Exact run `34486592055` completed SUCCESS.

## Highest current Backend gaps

### BE-046 — Emergency Reserve Windows directory-identity binding

Status: `OPEN / P1 / CURRENTLY REPRODUCED BY SOURCE TRACE`.

Current Develop still binds POSIX reserve creation/release to an opened parent directory FD. The non-POSIX branch still creates via `os.open(self.path, ...)`, validates pathname/file identity after open, and later performs cleanup/release through `self.path.stat()` / `self.path.unlink()`. Therefore directory identity is not bound through the Windows mutation itself. Preserve physical non-sparse allocation and exact release accounting; do not substitute weaker pathname-only checks.

### BE-052 — Preflight DB identity through live writer startup

Status: `OPEN / P1 / CURRENTLY REPRODUCED BY SOURCE TRACE`.

Current Develop `SQLiteDatabase.start()` still calls `inspect_database_read_only(self.path)` and then independently opens the writer with `sqlite3.connect(self.path, ...)`. The identity verified by preflight is not carried into the writable SQLite connection. A second pathname preflight would not close the race; a cross-platform identity-bound writer strategy is still required.

No product mutation was made for BE-046 or BE-052 in this run. A fresh local checkout for required focused testing was attempted and failed transiently at DNS resolution (`Could not resolve host: github.com`). No fabricated focused PASS is claimed and no untested product commit was created.

## Previously closed dependency slices

- Native Windows durable-FS POSIX harness-isolation cluster: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN` at `7fa2108d820cfc5b48a9f92d42ffa61697b74818`, run `34522965434`.
- BE-038 Windows HANDLE-bound durable filesystem publication: `CLOSED_ON_DEVELOP / QUEUE_EVIDENCE_STALE`.
- Schema reinitialization harness regression: `CLOSED_ON_DEVELOP / CANONICAL_GREEN`.
- BE-020 runtime ModelSignature drift guard: `CLOSED_ON_DEVELOP / QUEUE_EVIDENCE_STALE`.
- Windows storage bootstrap reserve-path harness cluster: `CLOSED_ON_DEVELOP / EXACT_LANE_VERIFIED`.
- Windows packaged runtime contracts (pypdf/Frozen argv/two-EXE/process dispatch): `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`.
- Adaptive 2048-context reserve Windows contract: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`.
- Core/API ownership lifecycle Windows contract: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`.
- Core/API server lifecycle Windows contract: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`.

## Current Backend worker red state

The broad historical worker branch remains non-authoritative relative to current Develop. Its last known exact canonical red state contains worker-only schema-v41 / `research_delta_boundaries` history plus a separate Ruff import-order finding. Do not mechanically repair legacy fixtures to preserve that worker-only lineage.

Integrator has already required that broad Backend/Storage/Migration/Runtime history not be absorbed as a unit. Any surviving worker delta must be re-proven as a small current-Develop gap before mutation or integration.

## Preserved release guards

- No silent Tor-to-Direct fallback.
- Redirect/Auth/HTTPS/response-size boundaries remain fail-closed.
- WAL maintenance safety remains intact.
- pypdf packaging, Frozen argv and two-EXE topology remain guarded with exact Windows canonical evidence.
- Exactly one Desktop instance / bounded worker ownership-lifecycle contracts, including the API server lifecycle boundary, retain direct exact Windows canonical evidence.
- Adaptive 2048-context reserve remains guarded with direct exact Windows canonical evidence.
- Windows lane-lock/path-safety, duplicate-column/Core-startup/storage-bootstrap signatures remain protected and are only OPEN when reproduced on current exact-SHA evidence.
- No Skip/XFail, force push, history rewrite, main mutation, or mutation to `bnbgrs/ATHENA`.

## Integrator prerequisites

- Native Windows durable-FS harness-isolation cluster: CLOSED on Develop `7fa2108d820cfc5b48a9f92d42ffa61697b74818`; canonical Quality `34522965434 = SUCCESS`; no Backend cherry-pick required.
- Core/API server lifecycle Windows verification: CLOSED on Develop; no Backend cherry-pick required.
- Core/API ownership lifecycle Windows verification: CLOSED on Develop; no Backend cherry-pick required.
- Adaptive 2048-context reserve Windows verification: CLOSED on Develop; no Backend cherry-pick required.
- Windows packaged runtime verification cluster: CLOSED on Develop; no Backend cherry-pick required.
- BE-038 / BE-020 / schema-reinitialization / Windows bootstrap harness: CLOSED on Develop; do not duplicate.
- BE-046 and BE-052 remain OPEN and have no candidate in this handoff.
- Broad Backend worker history: `HOLD / NOT READY`.
- Do not integrate worker-only schema-v41/WAL/Runtime changes without a fresh bounded reconciliation against current Develop and exact focused/canonical evidence.

## Next Backend action

Consume the then-current Develop and Backend exact-SHA results first. If Develop remains green, take exactly one bounded current gap, preferring BE-046 before BE-052 unless newer exact-SHA evidence raises a higher-priority Backend/System failure. Required focused tests must run before any product commit; do not weaken Storage/Recovery/Security invariants to obtain green tests.
