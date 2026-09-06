# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next@86ab95c9bd31e52a8d65fd3b37f7c27556a6f3b9`.
- Error branch pre-sync head: `b8e050c9756299a70e8f5d4df0139ef54a5f08a0`.
- History-preserving NON-FORCE synchronization: `28017c9cfb1c39623dd860dcaf30ac099fdd0ada`, with parents prior Error head + exact Develop and exact Develop tree before Error mutation.
- Worker heads reviewed: Backend `bc622dcb0554d2449183afe2331669ab15c7c8ef`; Spec/Core `96c8f17d99017060238da27b51f6e59b77b9eafc`; UI `6558031bb31e5e35f5c8639bf4f5c8591f7fa250`; Integrator/Develop `86ab95c9bd31e52a8d65fd3b37f7c27556a6f3b9`.
- `main` and `bnbgrs/ATHENA` remained strictly read-only; no force update or history rewrite was used.

## Current error state

- OPEN: none.
- FIXED_PENDING_VERIFY: `ERR-0016`, `ERR-0017`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0017 — minimal Error-owned correction now exists

Current Develop still has the confirmed broken Personal-Memory import graph: `src/athena/memory/service.py` imports `ModelInferredMemoryProposal`, while current Develop `src/athena/memory/models.py` does not define it.

The latest Backend canonical run inspected this cycle, `34024809050@bc622dcb0554d2449183afe2331669ab15c7c8ef`, remains red with the same primary cascade: mypy failure, pytest import-collection failure, Linux/Windows API runtime path-boundary failure and local Core/API restart failure. These remain one `ERR-0017` root cause, not separate error IDs.

The active Spec/Core worker supplies exact-green compatible evidence: `postmerge/spec-core@96c8f17d99017060238da27b51f6e59b77b9eafc`, canonical Quality `34024071953 = success`. Its proposal model enforces MODEL_INFERRED mode, confidence, NORMAL sensitivity, real UUID model/processing provenance and exact `review_required=True`.

To satisfy the hard progress rule without weakening product semantics, Error now carries that minimal compatible correction on top of exact current Develop:

- synchronization merge: `28017c9cfb1c39623dd860dcaf30ac099fdd0ada`;
- product fix: `5ff326e39611a3aea5678e2151c300822ad593f9` (`src/athena/memory/models.py`);
- focused provenance regression: `281cedc6010617ce0aa60ea25ec497500225bb17` (`tests/unit/test_personal_memory_inferred_provenance_validation.py`).

`ERR-0017` is therefore `FIXED_PENDING_VERIFY`, not `FIXED`. No PASS is claimed until the Error candidate itself completes real verification.

## Verification required for ERR-0017

Require on the exact corrected Error descendant:

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

On the corrected Error lineage, rerun focused poisoning, oversize-accounting, exact-limit/EOF and negative-read regressions. Close `ERR-0016` only when its signature remains absent under real focused/canonical verification.

## Integrator handoff

- Do not promote current Develop while `ERR-0017` remains present there.
- Preferred bounded correction is the exact model/test semantic delta represented by Error commits `5ff326e39611a3aea5678e2151c300822ad593f9` + `281cedc6010617ce0aa60ea25ec497500225bb17`, cross-checked against exact-green Spec/Core `96c8f17d99017060238da27b51f6e59b77b9eafc` / Quality `34024071953`.
- Accept `ERR-0017` as fixed only after exact candidate verification; then reverify `ERR-0016` on the same lineage.
- Preserve all Provider/Transport byte-budget/deadline, Windows path, Storage, Security, Recovery and Human-Control guards.

## Persistent Beta/release regression knowledge

Retain as explicit release acceptance without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume exact Quality/focused verification for the new ERR-0017 Error candidate.
2. If green, mark `ERR-0017` FIXED and reverify/close `ERR-0016` on that same lineage.
3. If red, deduplicate the exact primary diagnostic and fix the smallest real root cause without guard weakening.
4. After both closures, immediately consume the next real canonical/runtime failure signal.
