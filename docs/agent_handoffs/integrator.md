# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `270f97c36bd114036658e322f68d8011983ff150`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `7bfa470504a245889d21865831d75a73dcf9b068`; spec-core `374fb36ed5ecab2a23797e343a49e424ae394d21`; backend `75e45f99ce60b87e0b56ea024d3bed931ec461d4`; UI `8bf24a1d127df730ed563d15323c5a04118e62cb`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, history rewrite, auto-merge or main promotion was used.

## Progress this run — composer accessibility unblock

No current worker product slice was READY at review time: Core §65 exact Quality `34250365477` was cancelled and its synchronized head run `34250419847` remained in progress; Backend exact v41 facade Quality `34251782009` was cancelled and current head run `34251875708` remained pending; UI current head Quality `34252450993` remained pending.

Under progress rule C, the bounded UI accessibility slice from commits `7107fc5bf65fa184178713942d122c26e600aef8` + `8bf24a1d127df730ed563d15323c5a04118e62cb` was independently reviewed and transplanted onto Develop as `a7f91262df194bea0a3c8588bda062b75d4ce167`. Only `src/athena/desktop/pathena_startup_experience_2900.py` and `tests/unit/test_pathena_startup_experience_2900.py` changed: Ground and response-details controls now mirror their existing tooltips into `accessibleDescription`, with a focused regression asserting exact equality. No product copy, action behavior, Core, Backend, Storage, Security, scheduler/worker, packaging or Windows-runtime semantics changed.

Exact compare from the prior Develop head is ahead-only by one commit, two files, +25/-0. No Skip/XFail or assertion weakening was introduced. The current UI canonical run is still pending, so no global-green or promotion-ready claim is made.

## Current quality/error state

- Error handoff now splits exact Backend v41 failures into `ERR-0026` schema import ordering, `ERR-0027` missing v41 schema facade re-export, `ERR-0028` stale v40-shaped fixtures/expectations, and `ERR-0029` WAL test collaborator drift; `ERR-0025` remains the older independent pytest-only family.
- Backend v41 must remain held until exact Ruff/schema/WAL evidence is green; production migration and exact-type guards must not be weakened.
- `ERR-0023` remains `FIXED_PENDING_VERIFY` until exact Develop canonical green evidence exists.
- All eleven screens remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no pixel-level `MATCH` claim is made.

## Next integration order

1. Consume UI Quality `34252450993`, Backend `34251875708`, and Core `34250419847` when completed; integrate exactly one compatible READY successor.
2. Prefer exact-green Backend v41 recovery because it unblocks Spec/Core §75 durable Delta composition; do not integrate red schema/WAL lineage.
3. Obtain exact-current-Develop canonical verification for the descendant carrying `a7f91262df194bea0a3c8588bda062b75d4ce167`.
4. Preserve the release crash-regression matrix before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
