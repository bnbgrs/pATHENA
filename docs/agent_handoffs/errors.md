# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next@8de698904c98cb50de327e805ae8e9b600df11ea`.
- Error branch history-preserving NON-FORCE synchronization: `71ffb960d2641a3c3aa4ca80adce66b8072008a9`, parents prior Error head `61a65244ecd31797f47b7af1a454c3188193e2d5` + exact Develop `8de698904c98cb50de327e805ae8e9b600df11ea`.
- Worker heads reviewed: Backend `e7e8d46e4d1011ec5586367f086c1571fe2a1267`; Spec/Core `a4180a04a2e2f1e3abacdf62af954775c1bd5058`; UI `81b8d6c2c250a412bb2947b2b356d9111c10b995`; Integrator/Develop `8de698904c98cb50de327e805ae8e9b600df11ea`.
- `main` and `bnbgrs/ATHENA` remained strictly read-only; no force update or history rewrite was used.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Current canonical evidence

- Backend `postmerge/backend@e7e8d46e4d1011ec5586367f086c1571fe2a1267`, canonical Quality `34039538125 = success`: Local install smoke PASS; Validator PASS; Ruff PASS; mypy PASS; full pytest PASS; Linux storage and API runtime path-boundary regressions PASS; Windows locality/storage and API runtime path-boundary regressions PASS. No current ERR signature is present.
- Spec/Core `postmerge/spec-core@a4180a04a2e2f1e3abacdf62af954775c1bd5058`, canonical Quality `34038748816 = success`; no error-owned primary failure is established.
- UI `postmerge/ui@81b8d6c2c250a412bb2947b2b356d9111c10b995`, canonical Quality `34040342678` remains pending; no failure evidence exists yet.
- Current Develop `8de698904c98cb50de327e805ae8e9b600df11ea` has no exact completed canonical Quality observed in this run and is therefore not promotion-ready by Error criteria.

## Verified closures retained

`ERR-0016` and `ERR-0017` remain FIXED on corrected-lineage canonical Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe = success`; no exact-current contradictory evidence reopens them. `ERR-0004` remains FIXED; `ERR-0014` remains STALE absent exact recurrence.

## Integrator handoff

- Backend head `e7e8d46e4d1011ec5586367f086c1571fe2a1267` is exact-canonical-green and may be evaluated as a verified worker candidate under normal bounded integration rules; no Error-ledger objection is present.
- Spec/Core head `a4180a04a2e2f1e3abacdf62af954775c1bd5058` is also exact-canonical-green and has no Error-ledger objection.
- Do not consume UI `81b8d6c2c250a412bb2947b2b356d9111c10b995` as exact-green until Quality `34040342678` completes successfully.
- Do not reopen or reapply `ERR-0016` / `ERR-0017` absent exact-current contradictory evidence.
- Preserve Provider/Transport byte-budget/deadline/poisoning semantics, Personal-Memory provenance/review controls, Windows path safety, Storage, Security and Recovery guards.
- Current Develop still requires its own exact-SHA completed canonical evidence before promotion/readiness.

## Persistent Beta/release regression knowledge

Retain as explicit release acceptance without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume UI Quality `34040342678` to completion.
2. Check the next exact current Develop/worker canonical or runtime signal.
3. Deduplicate against the ledger and persistent crash matrix.
4. On a concrete primary failure, finalize root cause and either perform the minimal Error-owned fix or concretely verify the responsible worker correction in the same run.
