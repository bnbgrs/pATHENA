# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@c775d37f50e332639007ba162b4ff7f591434f1c`.
- Error worker: `postmerge/errors` only.
- Previous history-preserving NON-FORCE synchronization: `2778583a47a0a123911d4cddb4c700d6a8e61ef2`.
- Current Spec/Core head reviewed: `3b425e527fd701a984ee723c310ac86be062022d`; failing acceptance SHA `5fbe0dc8b3d7674a18c562e96c118ddf4e476985`.
- Current Backend head reviewed: `5df50d524d4177a2fe157cf18cb952ff15df65a4`.
- Current UI head reviewed: `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0024`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0024 — Spec/Core §72 unavailable-NAS acceptance pytest-only failure

Canonical Quality `34186455107` on exact `postmerge/spec-core@5fbe0dc8b3d7674a18c562e96c118ddf4e476985` completed failure. Local install, Windows path safety, Linux storage, Validator, Ruff and mypy all passed; only full pytest failed.

The exact delta is the new real orchestration acceptance `tests/unit/test_exhaustive_research_unavailable_nas.py`. It freezes three Research sources and requires one SUCCESSFUL, one IRRELEVANT and one UNAVAILABLE terminal work item to persist with coverage `2/3` and the unavailable item never reclassified as irrelevant.

The exact failing assertion/traceback is not exposed by the available connector. Local focused execution was attempted, but the runtime cannot currently resolve `github.com`; no speculative product-vs-harness classification and no false PASS are recorded.

Hard-progress handoff: next Error run must consume the exact diagnostic or a concrete repaired Spec/Core successor and finalize root cause / verify the owner mutation. Do not merely restate the unknown failure.

Integrator: HOLD §72 SHA `5fbe0dc8b3d7674a18c562e96c118ddf4e476985`; not READY.

## ERR-0023 — terminal Jobs reason uses forbidden implementation wording

Backend exact SHA `076a0d1209fe1cb30c6cfe7f6735a39158036c28` failed Quality `34177086068` only in full pytest because visible terminal-state reason contained `lifecycle action`.

Root cause is product copy in `src/athena/desktop/jobs_lifecycle.py`, not the harness. Error fix `d0207d43dabd66406df630a2cdff89e6f56b259b` changes only terminal copy to `This job is {state}; no actions are available.` and preserves lifecycle semantics and assertions.

Integrator has now applied that exact one-line correction to Develop as `568d57a63bb2253d97ca63e92b52e1df66505ac9`; current Develop `c775d37f50e332639007ba162b4ff7f591434f1c` retains it. Status remains `FIXED_PENDING_VERIFY` because no exact canonical Quality run exists yet for that Develop blob.

Independent UI successor `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8` humanizes the same terminal copy to `no job actions are available` and passed canonical Quality `34187727628 = success`. This confirms the defect class is cleared on the UI successor but is not substituted for exact verification of the integrated Error wording.

## Current worker evidence

- Spec/Core predecessor `b6fab29930459642ab41b42970ca87b92f4e563d` was exact-green via `34183001443`; new §72 SHA `5fbe0dc8b3d7674a18c562e96c118ddf4e476985` is exact-red via `34186455107` full-pytest only.
- Backend `5df50d524d4177a2fe157cf18cb952ff15df65a4`: Quality `34187200684` remains in progress; no PASS/FAIL inferred.
- UI `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8`: Quality `34187727628 = success`.
- Develop `c775d37f50e332639007ba162b4ff7f591434f1c`: integrated ERR-0023 correction present; no exact completed PR-triggered canonical Quality run associated with this SHA.
- No current exact-SHA reproduction of historical Windows/runtime crash signatures.

## Fix / coordination commits

- ERR-0023 product fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`.
- Develop integration of ERR-0023: `568d57a63bb2253d97ca63e92b52e1df66505ac9`.
- Current Error ledger refresh: `3bad1cb958c2ac184ae7c3995bd8936dd00abcfb`.

## Integrator handoff

- Keep `ERR-0023` at `FIXED_PENDING_VERIFY` until focused Jobs lifecycle + Ruff + exact canonical Quality succeeds on a Develop descendant carrying the Error-owned `no actions are available` blob.
- HOLD Spec/Core §72 `5fbe0dc8b3d7674a18c562e96c118ddf4e476985` for `ERR-0024`; repair only the demonstrated exact pytest defect once the assertion/traceback is available.
- UI `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8` is exact-green via `34187727628`; do not allocate a UI error from the earlier red predecessor.
- Consume Backend `34187200684` when it completes.
- No global Develop promotion-ready claim.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Finalize `ERR-0024` from exact pytest diagnostic or concrete repaired Spec/Core successor.
2. Verify integrated `ERR-0023` on exact Develop descendant with focused Jobs lifecycle, Ruff and canonical Quality.
3. Consume Backend `34187200684` on completion and next current runtime signal.
4. Before Beta/release promotion, run the known-crash matrix on the exact candidate SHA.
