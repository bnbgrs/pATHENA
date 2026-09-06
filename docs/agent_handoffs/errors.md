# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next@be0e8da5127f17f6bbc3cbbc8c58496102c9135c`.
- Error branch history-preserving NON-FORCE synchronization: `632ce8aa789e3b8c0760a87fb953597c5a1ac897`, parents prior Error head `59a45e490f130199a6177416f2ac9a06332053d2` + exact Develop `be0e8da5127f17f6bbc3cbbc8c58496102c9135c`.
- Worker heads reviewed: Backend `a424e32621d2c7441a144ff3a1a3faecd32ea7c4`; Spec/Core `c995fd2c4c6c369359dbdb09cedb43a8e74f535c`; UI `d955ccd53e3e2c7f98af0f6f3838be1ffa9b6fe6`; Integrator/Develop `be0e8da5127f17f6bbc3cbbc8c58496102c9135c`.
- `main` and `bnbgrs/ATHENA` remained strictly read-only; no force update or history rewrite was used.

## Current error state

- OPEN: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0017 — FIXED on corrected lineage

The Personal-Memory import-graph defect is now closed with real corrected-lineage evidence. The compatible `ModelInferredMemoryProposal` dependency is present together with MODEL_INFERRED mode, confidence, NORMAL sensitivity, real UUID provenance and exact `review_required=True` validation.

Canonical Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe = success`. Its four jobs all complete successfully. Python 3.12 quality passes specification Validator, Ruff, mypy and full pytest. Local install smoke passes disposable Core/API restart. Linux storage passes focused storage plus API runtime path-boundary regressions. Windows path safety passes locality, storage-path and API runtime path-boundary regressions.

The prior mypy/import-collection/API-path/startup cascade is absent on this exact corrected descendant. `ERR-0017` is therefore `FIXED`, not merely structurally repaired.

Do not remove the service import, weaken UUID/review/provenance validation, fabricate provenance, or bypass review-gated inference semantics.

## ERR-0016 — FIXED on the same corrected lineage

Backend product fix `d721846ea9524ab18336ba72eeb082cca7ee0fb8` plus regression `44bf215b999e727514fc10ddb88eb8379a5358b6` establishes explicit fail-closed poisoning after overflow without counting rejected bytes as successful consumption.

The same corrected-lineage canonical Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe = success` includes the Local HTTP response-boundary/oversize regression files in the successful full pytest execution, together with Ruff and mypy. The two poisoning failures reproduced in `34016515174` and `34019237735` do not recur. `ERR-0016` is now `FIXED`.

Preserve the explicit poisoned state, `remaining + 1` overflow probe, exact-limit/EOF behavior, negative integer read acceptance, byte-budget/deadline/type validation and loopback/proxy/redirect guards.

## Current Develop quality status

Integrator composed the verified corrected-lineage Local HTTP blobs onto Develop in `3376fac0051483308d8c24e1e58d6b532bde702e` and recorded that in current Develop head `be0e8da5127f17f6bbc3cbbc8c58496102c9135c`.

No exact canonical Quality run for current Develop head `be0e8da5127f17f6bbc3cbbc8c58496102c9135c` was observed in this Error run. Therefore this handoff closes the two defect IDs but does **not** claim current Develop or any release candidate promotion-ready.

## Integrator handoff

- Accept `ERR-0017` as FIXED based on corrected-lineage Quality `34030367660` and do not reapply the model dependency.
- Accept `ERR-0016` as FIXED on the same exact corrected lineage; preserve all verified Local HTTP boundary semantics.
- Current Develop still needs its own exact-SHA canonical Quality before promotion/readiness.
- Consume the next real canonical/runtime failure only; do not manufacture a new error from documentation-only or old-base failures.
- Preserve all Provider/Transport byte-budget/deadline, Windows path, Storage, Security, Recovery and Human-Control guards.

## Persistent Beta/release regression knowledge

Retain as explicit release acceptance without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume the next exact canonical Quality/runtime signal on current Develop or active worker corrected descendants.
2. Deduplicate any failure against the existing ledger and persistent crash matrix.
3. On a concrete primary failure, finalize root cause and either perform the minimal Error-owned fix or concretely verify the responsible active worker correction in the same run.
4. Keep current Develop non-promotion-ready until its exact head receives completed canonical evidence.
