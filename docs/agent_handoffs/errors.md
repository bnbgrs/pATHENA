# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA observed this run: `cf33955bcaa91649f2b5ac1142940e5e72ffa43a`
- Worker branch: `postmerge/errors`
- History-preserving NON-FORCE synchronization: `4c26809ce681afaa8d08bb1983c1b71f2975e237`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0010`.
- FIXED: `ERR-0001` through `ERR-0009`, `ERR-0011`.
- BLOCKED: none.

## Fresh evidence

- Backend Quality `33933291735` on `4adcf14dc67a617a4a2a5ff942cc600e40aaf456` completed `failure`. Diagnostics artifact `9959994409` shows one primary failure only: `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_enforces_monotonic_total_deadline`, `TimeoutError`, total `1 failed, 4625 passed, 3 skipped, 2 warnings`.
- UI Quality `33933890301` on `2193332eeb3a390c263baa66e83324ff70a61168` also completed `failure`; successor UI Quality `33936799048` on `62e217098f60fe3d1417b5572947abc7fc5b4b40` reproduces the exact same single node with `1 failed, 4627 passed, 3 skipped, 2 warnings`. Its validator, Ruff, mypy, Windows path safety, Linux storage and local-install jobs are PASS.
- These are not `ERR-0012`: they are recurrent `ERR-0010` caused by stale harness timing after direct `readline()` deadline checks. Product fail-closed timeout behavior is not the defect.
- Current Develop still contains the stale four-timestamp fixture `[10.0, 10.2, 10.6, 11.0]` together with iterator + direct-read pre/post deadline checks, so no exact-head global-green claim is permitted.
- UI owner head `f6d2b3afe58fcb0552a0fbd7c72737c2038b18b0` has the minimal harness-only correction `[10.0, 10.2, 10.4, 10.6, 10.8, 11.0]`; Quality `33937005854` is in progress.
- Backend owner head `dd1311dfeec02030fe6e05f6bd8a81fc13f5fce0` carries the corresponding correction lineage; Quality `33936396203` is in progress.

## Collision avoidance

- Do not mutate the deadline product guard in `src/athena/model/adapters/local_http.py`.
- UI/Backend currently own the colliding harness correction in `tests/unit/test_lm_studio_response_limits.py`; Error therefore does not race their active mutations this cycle.
- If both owner corrections fail or disappear after a full worker cycle and no active collision remains, Error may apply only the already proven six-timestamp harness correction.
- No skip/XFail, assertion weakening, mock-success path, byte-cap weakening, transport relaxation, storage/recovery change or security relaxation is allowed.

## Integrator handoff

- `ERR-0001` through `ERR-0009` and `ERR-0011` remain cleared on their recorded evidence.
- Treat `ERR-0010` as `FIXED_PENDING_VERIFY` because its exact signature recurred on current worker lineages and current Develop still carries the stale timing fixture.
- Reject Backend `4adcf14dc67a617a4a2a5ff942cc600e40aaf456`, UI `2193332eeb3a390c263baa66e83324ff70a61168`, and UI `62e217098f60fe3d1417b5572947abc7fc5b4b40` as globally green.
- Do not integrate the stale four-timestamp fixture. Prefer an exact-green owner correction from UI `f6d2b3afe58fcb0552a0fbd7c72737c2038b18b0` / Backend `dd1311dfeec02030fe6e05f6bd8a81fc13f5fce0`, then rerun canonical Quality on resulting exact Develop SHA.
- Preserve the direct total-deadline, cumulative byte-budget, loopback-only/proxy-free transport, storage/recovery and security guards.

## Next scan

1. Consume Backend `33936396203` and UI `33937005854`.
2. Close `ERR-0010` only after exact corrected owner-head canonical success and preserved correction on Develop.
3. If either run is red, isolate the new primary signature and deduplicate before mutation.
4. Otherwise continue Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt/Desktop, Security, Windows path safety, Linux storage and local install/start scanning.
