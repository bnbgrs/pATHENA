# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next@70f985ce7a28044824bfbfa53769b982fa152747`.
- Error branch history-preserving NON-FORCE synchronization: `63b43664c5fd87d7d9672bff880d2804efb15b9f`, parents prior Error head `ea77cc03ce1d5c6a27286ac6c7cba38a7ce6566e` + exact Develop `70f985ce7a28044824bfbfa53769b982fa152747`.
- Worker heads reviewed: Backend `8964f9ae22f0b3f98d06f9c000a47a98dc54f473`; Spec/Core `07263cc7474954f1591523077caa8eb8532605dd`; UI `0d5a89b879ee0959a42734181adb129f4c3de024`; Integrator/Develop `70f985ce7a28044824bfbfa53769b982fa152747`.
- `main` and `bnbgrs/ATHENA` remained strictly read-only; no force update or history rewrite was used.

## Current error state

- OPEN: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Verified closures retained

`ERR-0016` and `ERR-0017` remain FIXED on corrected-lineage canonical Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe = success`; no current exact-SHA evidence reopens either defect. `ERR-0004` remains FIXED and `ERR-0014` remains STALE absent exact-current reproduction.

## Current canonical evidence

- Backend `postmerge/backend@8964f9ae22f0b3f98d06f9c000a47a98dc54f473`, Quality `34033392294`: Windows path safety PASS, Linux storage regressions PASS, local install smoke PASS, Validator PASS, Ruff PASS, mypy PASS; full pytest remains IN_PROGRESS. No concrete primary failure is established.
- UI `postmerge/ui@0d5a89b879ee0959a42734181adb129f4c3de024`, Quality `34034051224`: run is pending/queued and has not produced job evidence yet. The immediately prior superseded UI run was cancelled, not failure evidence.
- Current Develop `70f985ce7a28044824bfbfa53769b982fa152747` has advanced with UI-GAP-0039 integration. No exact completed canonical Quality for this exact Develop SHA was observed in this run; therefore it is not promotion-ready by Error criteria.

## Integrator handoff

- Do not reopen or reapply `ERR-0016` / `ERR-0017` absent exact-current contradictory evidence.
- Consume completion of Backend Quality `34033392294` and UI Quality `34034051224`; allocate/reopen an ERR only for a concrete deduplicated primary failure.
- Preserve Provider/Transport byte-budget/deadline and poisoning semantics, Personal-Memory provenance/review controls, Windows path safety, Storage, Security and Recovery guards.
- Current Develop still requires its own exact-SHA completed canonical evidence before promotion/readiness.

## Persistent Beta/release regression knowledge

Retain as explicit release acceptance without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume Backend Quality `34033392294` and UI Quality `34034051224` to completion.
2. Check the next exact current Develop/worker canonical or runtime signal.
3. Deduplicate against the ledger and persistent crash matrix.
4. On a concrete primary failure, finalize root cause and either perform the minimal Error-owned fix or concretely verify the responsible worker correction in the same run.
