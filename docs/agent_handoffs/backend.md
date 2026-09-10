# Backend & Systems Handoff

Generated: 2026-09-10
Branch: `postmerge/backend`

## Current source of truth

- Develop consumed first: `develop/pathena-next@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17`.
- Backend worker head before this handoff refresh: `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2`.
- Exact Develop canonical Quality `34468185990@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17 = SUCCESS`.
- Exact Backend canonical Quality `34455900467@7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2 = FAILURE`; no worker Quality run was queued or in progress when this refresh began.
- Current Develop handoffs/spec-core/UI/integrator handoffs and current Alpha/Beta/architecture/runtime/storage documentation were treated as authoritative over historical worker priorities.

## Closed dependency slice — BE-038 Windows HANDLE-bound durable filesystem publication

Status: `CLOSED_ON_DEVELOP / QUEUE_EVIDENCE_STALE`.

The persistent Backend queue still describes Windows durable publication as pathname-based `MoveFileExW` and marks BE-038 READY. That evidence is stale on current Develop.

On `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17`, `src/athena/storage/durable_fs.py` implements `_windows_open_bound_handle()` with `CreateFileW(..., FILE_FLAG_OPEN_REPARSE_POINT)` and validates reparse state, expected file/directory type, and final path identity before returning the HANDLE. `_windows_replace_write_through()` binds both the source object and destination parent to HANDLE identities, then `_windows_rename_relative()` performs the publication relative to the bound destination parent via `NtSetInformationFile(FileRenameInformation)`. The destination is constrained to one plain leaf name.

Therefore the pathname-based Windows publication gap described by BE-038 is already closed on authoritative Develop and must not cause another Backend implementation of the same primitive. The exact Develop canonical Quality for the inspected SHA is green.

No production code, test assertion, filesystem guard, Storage/Recovery behavior, or security boundary was changed for this closure.

## Closed dependency slice — schema reinitialization harness regression

Status: `CLOSED_ON_DEVELOP / CANONICAL_GREEN`.

The prior `test_schema_reinitialization_contract.py` harness regression is closed on Develop `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17`. The harness retains `sqlite3.Row` for named schema-verification access and compares `PRAGMA user_version` by scalar value. Canonical Quality `34468185990` completed SUCCESS. No production migration or schema guard change is required.

## Previously closed dependency slice — BE-020 runtime ModelSignature drift guard

Status: `CLOSED_ON_DEVELOP / QUEUE_EVIDENCE_STALE`.

The persistent Backend queue still states that shared `chat/generation.py` uses an older inline signature comparison. That statement is stale on current Develop. The reusable revision-aware ModelSignature guard is already wired before provider dispatch. Do not duplicate it.

## Previously closed root-cause cluster — Windows storage bootstrap reserve path

Status: `CLOSED_ON_DEVELOP / EXACT_LANE_VERIFIED`.

The earlier Windows storage-bootstrap harness defect was fixed on authoritative Develop. The failing test stub used a POSIX-looking `/tmp/...` path that was not absolute on Windows; production `EmergencyReserveStatus` correctly rejected it fail-closed. The corrected test uses a platform-valid absolute path. No production Storage/Recovery behavior was weakened.

## Current Backend worker red state

The broad historical worker branch remains non-authoritative relative to current Develop. Its last exact canonical run is red and contains worker-only schema-v41 / `research_delta_boundaries` history plus a separate Ruff import-order finding. Do not mechanically repair legacy fixtures to preserve that worker-only schema lineage.

Integrator has already required that broad Backend/Storage/Migration/Runtime history not be absorbed as a unit. Any surviving worker delta must be re-proven as a small current-Develop gap before mutation or integration.

## CI discipline / verification constraints

- No Backend canonical Quality run was queued or in progress on `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2` when this handoff refresh began; `34455900467` is completed FAILURE.
- A fresh local checkout was attempted again in this run and remains blocked by transient DNS resolution of `github.com`; focused local pytest/Ruff execution is therefore unavailable.
- This run made no product/test mutation and claims no fabricated focused PASS. BE-038 closure is based on direct exact-SHA source inspection plus the completed exact-SHA green canonical Develop run.
- Any future product/test mutation must begin with current Develop/worker/run re-check and obtain real focused verification before canonical Quality.

## Preserved release guards

- No silent Tor-to-Direct fallback.
- Redirect/Auth/HTTPS/response-size boundaries remain fail-closed.
- WAL maintenance safety remains intact.
- pypdf packaging, Frozen argv and two-EXE topology remain guarded.
- Bounded worker tree and adaptive 2048-context reserve remain guarded.
- Windows lane-lock/path-safety, duplicate-column/Core-startup/storage-bootstrap signatures remain protected and are only OPEN when reproduced on current exact-SHA evidence.
- No Skip/XFail, force push, history rewrite, main mutation, or mutation to `bnbgrs/ATHENA`.

## Integrator prerequisites

- BE-038: CLOSED on Develop `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17`; no Backend product cherry-pick is required.
- Schema reinitialization harness cluster: CLOSED on Develop `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17`; canonical Quality `34468185990 = SUCCESS`.
- BE-020: CLOSED on Develop; no Backend product cherry-pick is required.
- Windows storage bootstrap reserve-path cluster: CLOSED on Develop; no further Backend action required.
- Broad Backend worker history: `HOLD / NOT READY`.
- Do not integrate worker-only schema-v41/WAL/Runtime changes without a fresh bounded reconciliation against current Develop and exact focused/canonical evidence.

## Next Backend action

Consume the then-current Develop and Backend exact-SHA results first. Ignore BE-038 and BE-020 as stale queue work. Select the highest still-authoritative Backend/System gap from current red exact-SHA evidence or current specs/contracts. Do not preserve historical worker-only behavior merely to make its old tests green.
