# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `ee940a135e0859b3d880d44d873260f0617b17f4`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `54abf5b205473c29b1c757442b9e6db09ee68e2c`; spec-core `af1f9da019fbee21984cf62fb77a2e8bbacaed5b`; backend `8929474b6bdc4885c51e51de327816d5cf42137c`; UI `6cd161d98a54ebfa0c356fe0a3c21660fc1a9812`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, rebase, history rewrite, auto-merge or main promotion was used.

## Progress this run — UI-GAP-0075 Jobs process-error copy

No current worker head was fully READY at review: Backend exact Quality on `9c458e2c4af09a54df234cd518f6e82b84ad34f8` was cancelled (`34206121680`), current UI merge-head Quality `34205607335` remained in progress, and predecessor UI Quality `34200490506` failed. The hard progress rule therefore used a previously deferred exact-green bounded UI slice.

- Product commit: `86444c8a762f910d9929f50841f78376312a0afe` (`fix(ui): humanize Jobs process errors`).
- Focused-test commit: `9af7d23d2daccdee78236b6da335090d512d7fcd`.
- Exact successful descendant: `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8`; ATHENA Quality Gate `34187727628 = success`.
- Git ancestry check proves `9af7d23d2daccdee78236b6da335090d512d7fcd` is an ancestor of that exact-green descendant (`ahead_by=6`, `behind_by=0`).
- Develop integration commit: `06c837c59c499d20c26bbdd9467501849f88c09a`.

The bounded change replaces implementation-facing QProcess error text with operation-facing product copy. List failures say `Jobs refresh ...`, show failures say `Job details ...`, and lifecycle actions retain the explicit operation/job/error identity. The focused Qt regression forbids visible `jobs command` / `local jobs command` wording. QProcess spawning, operation identity, action availability, receipts, scheduler/worker behavior, persistence, Storage, Security, Recovery, packaging and Windows runtime semantics are unchanged.

The two imported blobs are exactly the worker product/test blobs. Comparing the exact-green descendant against the focused-test commit shows only later integrator docs, terminal Jobs lifecycle wording, and independent Spec/Core acceptance additions; the imported `jobs_workspace.py` and `test_pathena_jobs_status_copy.py` were unchanged after `9af7d23...` on that green lineage.

## Verification state

- `UI-GAP-0075` exact worker lineage is green through Quality `34187727628` on `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8`.
- Current Develop after product/test integration is `06c837c59c499d20c26bbdd9467501849f88c09a` before this handoff documentation commit.
- No exact-current-Develop canonical Quality has yet completed on the new descendant; global-green/promotion-ready is not claimed.
- No Skip/XFail, assertion weakening or guard relaxation was introduced.

## Other worker state

- Error head `54abf5b205473c29b1c757442b9e6db09ee68e2c`: `ERR-0024` is closed; `ERR-0025` tracks the Backend pytest-only failure; `ERR-0023` remains FIXED_PENDING_VERIFY until exact Develop verification.
- Spec/Core head `af1f9da019fbee21984cf62fb77a2e8bbacaed5b`: §72 exact-green repair already integrated previously; no additional Core slice consumed this run.
- Backend head `8929474b6bdc4885c51e51de327816d5cf42137c`: canonical WAL-hook exact-type boundary lacks successful exact Quality because run `34206121680` was cancelled; not READY.
- UI head `6cd161d98a54ebfa0c356fe0a3c21660fc1a9812`: synchronized with current Develop baseline, but run `34205607335` was still in progress at review; not consumed.

## UI / Alpha-Beta state

- Eleven-screen status remains implemented pending visual review; no MATCH claim is made without original-reference evidence.
- `docs/development/ALPHA_BETA_PROGRESS.md` remains the canonical tracker. No percentage is inferred. The connector does not expose a safe complete replacement body for the large tracker in this run, so no destructive partial rewrite was attempted; this handoff records the exact evidence for the next safe tracker update.
- No historical Windows/runtime crash class is reopened without exact-current reproduction.

## Next integration order

1. Obtain exact-current-Develop focused Jobs regressions, Ruff and canonical Quality on a descendant carrying `06c837c59c499d20c26bbdd9467501849f88c09a`.
2. Close `ERR-0023` only if that exact Develop evidence is green; consume any concrete `ERR-0025` traceback/successor before attributing the Backend failure.
3. Integrate exactly one compatible READY successor: prefer current UI only after exact-green completion, otherwise Backend WAL-hook boundary after exact-green evidence, otherwise a new bounded Core successor.
4. Preserve the release crash-regression matrix before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
