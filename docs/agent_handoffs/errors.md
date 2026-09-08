# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@b5f824082fcd9d335ea55de76f88d23a3c0ee7e8`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE sync this run: `0245da229e2a62b12b1d0404f34c729a5aa59319`.
- Current Spec/Core head: `147d9527ff06ce772aa378e29befa00d77031e9e`.
- Current Backend head: `ea601b96d681580c2e8f1f1af40c7d97c347511e`.
- Current UI head: `bcce837f347f8b67f3b4de1ab465f3e80c750eea`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0024`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## ERR-0024 — §72 unavailable-NAS acceptance

Initial exact failure: Spec/Core `5fbe0dc8b3d7674a18c562e96c118ddf4e476985`, Quality `34186455107`; only full pytest failed.

The first demonstrated harness defect is repaired: work-item identity is now resolved through candidate -> exact `source_id` instead of list position. Repair `124bdd9d789230d33452cfbc2452b307d410316c` retains the exact NAS source, UNAVAILABLE-not-IRRELEVANT semantics, processed=3, failed=0, 2/3 coverage and durable-state assertions.

That repair is conclusively insufficient to close the remaining canonical failure. Exact Quality `34190083267` on the repair failed only full pytest; unchanged handoff descendant `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00` failed `34190114472` only full pytest; current unchanged diagnostic descendant `147d9527ff06ce772aa378e29befa00d77031e9e` failed `34194199456` only full pytest. On the latest run, Local install, Windows path safety, Linux storage, specification validator, Ruff and mypy all passed.

Root-cause progress this run: list-order/source-identity is explicitly closed as the remaining primary cause. The second failure persists independently after the repair. GitHub job metadata proves only `Quality — pytest` fails and diagnostics upload succeeds; the available connector still cannot expose the uploaded diagnostics payload or pytest traceback, and local direct reproduction remains blocked by transient `github.com` DNS resolution. No speculative product-vs-harness patch is permitted without the exact remaining assertion.

Integrator: HOLD §72. Next Error run must consume the exact remaining pytest assertion/traceback or a concrete corrective successor and then finalize the second root cause or verify its minimal fix. Do not repeat the closed list-order hypothesis.

## ERR-0023 — terminal Jobs copy

Root cause remains product copy in `src/athena/desktop/jobs_lifecycle.py`; Error fix `d0207d43dabd66406df630a2cdff89e6f56b259b` changed terminal wording to `This job is {state}; no actions are available.`. Develop integration `568d57a63bb2253d97ca63e92b52e1df66505ac9` is an ancestor of current Develop `b5f824082fcd9d335ea55de76f88d23a3c0ee7e8`.

Status remains `FIXED_PENDING_VERIFY`: no completed canonical Quality on the current Develop descendant establishes exact verification of the integrated Error wording. Equivalent UI wording is not substituted for exact Develop verification.

## Current worker evidence

- Spec/Core `147d9527ff06ce772aa378e29befa00d77031e9e` -> Quality `34194199456 = failure`, pytest-only with all non-pytest gates green; deduplicated to `ERR-0024`.
- Backend product `efdae09dc71a661ea5c81f67b8e2b09ac90c0080` -> Quality `34195556143 = cancelled`; immediate handoff descendant `ea601b96d681580c2e8f1f1af40c7d97c347511e` -> Quality `34195601115 = in_progress`. Cancellation is not allocated as a defect.
- UI current `bcce837f347f8b67f3b4de1ab465f3e80c750eea` -> Quality `34195898979 = in_progress`.
- Develop `b5f824082fcd9d335ea55de76f88d23a3c0ee7e8`: no exact completed canonical Quality success establishing global promotion readiness.
- No exact-current reproduction of historical Windows/runtime crash signatures.

## Integrator handoff

- HOLD `ERR-0024` / Spec-Core §72 until the second full-pytest failure is exactly root-caused and a corrected exact successor is canonical green.
- Keep `ERR-0023` at `FIXED_PENDING_VERIFY` until focused Jobs lifecycle + Ruff + canonical Quality succeed on a Develop descendant carrying the exact Error-owned wording.
- Consume Backend `34195601115` and UI `34195898979` when complete; deduplicate any red signal before allocating a new ERR.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and release crash-regression guards.
- No global Develop promotion-ready claim.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume exact remaining §72 pytest evidence or a concrete corrective Spec/Core successor; finalize the second `ERR-0024` root cause or verify its fix.
2. Consume Backend `34195601115` and UI `34195898979`; deduplicate before opening any new ERR.
3. Verify integrated `ERR-0023` on an exact Develop descendant.
4. Before Beta/release promotion, execute the known-crash matrix on the exact candidate SHA.
