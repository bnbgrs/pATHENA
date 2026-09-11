# Backend & Systems Handoff

Generated: 2026-09-11
Branch: `postmerge/backend`

## Current source of truth

- Develop consumed first: `develop/pathena-next@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c`.
- Backend worker head before this handoff refresh: `44201f9dd2c1378c98afccc9a30ddf18c98b2405`.
- Exact Develop canonical Quality `34544225707@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c = SUCCESS`.
- The previous exact-SHA pytest-only failure at `4634bdf28c98bc114e0369701122818d474f99d9` is resolved on Develop by the bounded UI typography-contract test alignment. Backend does not duplicate or absorb that repair.
- No canonical Quality run was queued or in progress on the current Backend worker head when this refresh began; visible Backend runs were completed historical runs.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Current backend failure state

Status: `NO CURRENT EXACT-SHA BACKEND FAILURE / DEVELOP CANONICAL GREEN`.

The latest authoritative Develop head is canonical green. No current exact-SHA evidence justifies reopening historical Backend failures or weakening any Storage, Recovery, Security, runtime or test invariant.

## Highest current Backend gaps

### BE-046 — Emergency Reserve Windows directory-identity binding

Status: `OPEN / P1 / CURRENT SOURCE TRACE CONFIRMED`.

Current Develop preserves POSIX parent-directory-FD binding for reserve creation and release. The non-POSIX path still creates via `os.open(self.path, ...)`, validates file/path identity after opening, and performs failure cleanup and normal release via pathname `stat()` / `unlink()` operations. Therefore the reserve directory identity is not bound through the Windows mutation itself. Physical non-sparse allocation and exact release accounting must be preserved.

No product mutation was made in this run. The required focused-test path was attempted again from a fresh local checkout and remains transiently blocked by DNS resolution of `github.com` (`Could not resolve host: github.com`). No fabricated focused PASS and no untested Storage commit are claimed.

### BE-052 — Preflight DB identity through live writer startup

Status: `OPEN / P1 / CURRENT SOURCE TRACE CONFIRMED`.

Current `SQLiteDatabase.start()` still performs read-only preflight against the configured path and later opens the writable SQLite connection independently by pathname. The preflight filesystem identity is therefore not carried into the live writer. A second pathname preflight would not close the race; a cross-platform identity-bound writer strategy remains required.

BE-052 was not mutated because BE-046 remains the higher current bounded Backend target and no newer exact-SHA Backend failure supersedes it.

## Closed exact-evidence clusters

- Native Windows durable-FS POSIX harness isolation: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`, integrated at `7fa2108d820cfc5b48a9f92d42ffa61697b74818`, canonical run `34522965434 = SUCCESS`.
- Core/API server lifecycle Windows contract: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`, run `34510755656 = SUCCESS`.
- Core/API ownership lifecycle Windows contract: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`, run `34504620300 = SUCCESS`.
- Adaptive 2048-context reserve Windows contract: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`, run `34492275924 = SUCCESS`.
- Windows packaged runtime contracts including pypdf/Frozen argv/two-EXE: `CLOSED_ON_DEVELOP / EXACT_WINDOWS_EVIDENCE_GREEN`, run `34486592055 = SUCCESS`.
- BE-038 Windows HANDLE-bound durable filesystem publication: closed on current Develop; do not reopen without current exact-SHA reproduction.
- BE-020 runtime ModelSignature drift guard, schema reinitialization and Windows storage-bootstrap historical signatures: closed/stale unless reproduced on current exact-SHA evidence.

## Coordination

- Current Develop Errors handoff has no current OPEN error assigned there; do not duplicate closed Error-worker slices.
- Spec/Core owns normal-Hybrid Search facade/application composition and remains non-overlapping with BE-046/BE-052.
- UI owns visual hierarchy/composer/PALLAS work and the repaired typography test contract; Backend does not mutate those paths.
- Integrator explicitly keeps BE-046/BE-052 out of parallel integration until Backend produces a bounded candidate with focused adversarial identity evidence.

## Preserved release guards

- No silent Tor-to-Direct fallback.
- Redirect/Auth/HTTPS/response-size boundaries remain fail-closed.
- WAL maintenance remains SQLite-owned and safe.
- pypdf packaging, Frozen argv and two-EXE topology remain guarded.
- Exactly one Desktop instance / bounded worker ownership-lifecycle remains guarded.
- Adaptive 2048-context reserve remains guarded.
- Windows lane-lock/path-safety, duplicate-column/Core-startup/storage-bootstrap signatures remain protected.
- No Skip/XFail, force push, history rewrite, `main` mutation or mutation to `bnbgrs/ATHENA`.

## Integrator prerequisites

- Authoritative Develop: `7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c`, canonical Quality `34544225707 = SUCCESS`.
- Previous pytest-only red state at `4634bdf28c98bc114e0369701122818d474f99d9` is resolved and is not Backend-owned.
- BE-046 and BE-052 remain OPEN with no Backend product candidate in this handoff.
- Broad historical Backend worker history remains `HOLD / NOT READY`; do not absorb it as a unit.
- Any future Backend candidate must be a small current-Develop-compatible diff, pass real focused regressions first, preserve all Storage/Recovery/Security invariants, and obtain exact-SHA canonical evidence before READY.

## Next Backend action

Consume the then-current Develop head and exact-SHA Quality first. If still canonical green and no newer Backend failure exists, continue with exactly one bounded BE-046 closure attempt. Required focused tests must execute before a product commit; if the local test path remains transiently unavailable, do not create an untested Storage mutation. After BE-046 is safely closed, BE-052 is the next current P1 target unless newer exact-SHA evidence changes priority.
