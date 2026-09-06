# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next@b1537fc138560fe85d4d97cf76c887b92e63c8f4`.
- Error branch history-preserving NON-FORCE synchronization: `d01e73b889a8fa9e680fca3fb79fa5ce6c91f1bc`, parents prior Error head `f434f9f714f1453cac5fda8b1aa5b7f8684dedda` + exact Develop `b1537fc138560fe85d4d97cf76c887b92e63c8f4`.
- Worker heads reviewed: Backend `2a6d1ba76d4822e324bd8117fc001dd79667d702`; Spec/Core `b62e08cac198fde7ce7c5f081dd577decdcc216d`; UI `3d89bffeef82244361e701738ebc05862d1a2b64`; Integrator/Develop `b1537fc138560fe85d4d97cf76c887b92e63c8f4`.
- `main` and `bnbgrs/ATHENA` remained strictly read-only; no force update or history rewrite was used.

## Current error state

- OPEN: none.
- FIXED_PENDING_VERIFY: `ERR-0016`, `ERR-0017`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0017 — integrated on Develop, exact-current verification still required

The confirmed Personal-Memory import-graph defect is structurally repaired on current Develop. `src/athena/memory/models.py` now defines `ModelInferredMemoryProposal` with MODEL_INFERRED mode, confidence, NORMAL sensitivity, real UUID provenance and exact `review_required=True` validation. Integrator composed the bounded product/test blobs from exact-green Spec/Core evidence.

Integrator evidence: source `postmerge/spec-core@b62e08cac198fde7ce7c5f081dd577decdcc216d`; canonical Quality `34026871459 = success`; Develop product/test commits `a7a6301ec580492ee443d2c32e3d65ad624cdcc4`, `dbfcd37e7411447cb6abb4be29731908deff909e`, normalization `bda6aed03fd928e19c8bac3e1f5751e55c833bcc`, `8d56252a1c4da7ee2a59739659e6a4614fce7a2d`.

Current Develop head `b1537fc138560fe85d4d97cf76c887b92e63c8f4` has no exact canonical workflow run. Therefore `ERR-0017` remains `FIXED_PENDING_VERIFY`, not `FIXED`.

Backend `34027582618@2a6d1ba76d4822e324bd8117fc001dd79667d702` is red through the same old-base ERR-0017 cascade: Validator PASS and Ruff PASS, then mypy/import collection/API path-boundary/local Core restart failures. It is not a new independent error and does not reopen the repaired current-Develop import graph.

## Verification required for ERR-0017

Require on an exact corrected Develop descendant:

- specification Validator;
- Ruff;
- mypy;
- focused Personal-Memory inferred-proposal / review-acceptance / provenance tests;
- disposable local Core/API restart smoke;
- API runtime path-boundary regressions on Linux and Windows;
- full pytest;
- canonical ATHENA Quality completion.

Do not remove the service import, weaken UUID/review/provenance validation, fabricate provenance, or bypass review-gated inference semantics.

## ERR-0016 — reverify on the same corrected lineage

Backend fix `d721846ea9524ab18336ba72eeb082cca7ee0fb8` plus regression `44bf215b999e727514fc10ddb88eb8379a5358b6` implements explicit fail-closed poisoning after overflow without counting rejected bytes as successful consumption. Previous canonical closure was blocked by `ERR-0017`, not by recurrence of the poisoning signature.

On the corrected Develop lineage, rerun focused poisoning, oversize-accounting, exact-limit/EOF and negative-read regressions. Close `ERR-0016` only when its signature remains absent under real focused/canonical verification.

## Integrator handoff

- Do not claim promotion-ready for `b1537fc138560fe85d4d97cf76c887b92e63c8f4` without exact-current canonical verification.
- Structural ERR-0017 correction is already integrated; do not reapply or broaden it.
- Treat Backend run `34027582618` as an old-base ERR-0017 cascade, not a new error ID.
- First exact corrected-lineage Quality success may close ERR-0017 if focused/import/startup evidence is green; on that same lineage reverify ERR-0016 poisoning/oversize accounting.
- Preserve all Provider/Transport byte-budget/deadline, Windows path, Storage, Security, Recovery and Human-Control guards.

## Persistent Beta/release regression knowledge

Retain as explicit release acceptance without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume exact corrected-lineage canonical verification for ERR-0017.
2. If green, mark ERR-0017 FIXED and reverify/close ERR-0016 on the same lineage.
3. If red, deduplicate the exact primary diagnostic and fix the smallest real root cause without guard weakening.
4. After both closures, immediately consume the next real canonical/runtime failure signal.
