# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@b5f824082fcd9d335ea55de76f88d23a3c0ee7e8`.
- Error branch mutation lineage: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization this run: `0245da229e2a62b12b1d0404f34c729a5aa59319`, parents prior Error head `df2c48216aab958219db0db868c58e53ddcd6d4a` and current Develop `b5f824082fcd9d335ea55de76f88d23a3c0ee7e8`.
- Current Spec/Core head reviewed: `147d9527ff06ce772aa378e29befa00d77031e9e`.
- Current Backend head reviewed: `ea601b96d681580c2e8f1f1af40c7d97c347511e`.
- Current UI head reviewed: `bcce837f347f8b67f3b4de1ab465f3e80c750eea`.
- `main` and `bnbgrs/ATHENA` remained read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`.
- STALE: `ERR-0014`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- IN_PROGRESS: `ERR-0024`.
- OPEN/BLOCKED: none.

## ERR-0024 — Spec/Core §72 unavailable-NAS acceptance full-pytest failure

- Severity: P2.
- Status: `IN_PROGRESS`.
- Initial exact evidence: canonical Quality `34186455107` on `postmerge/spec-core@5fbe0dc8b3d7674a18c562e96c118ddf4e476985`; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS; full pytest FAIL only.
- Confirmed first harness defect: the original acceptance bound SUCCESSFUL/IRRELEVANT/UNAVAILABLE to work-list order, not exact source identity. Work-item list order is not source identity.
- Owner repair: `124bdd9d789230d33452cfbc2452b307d410316c` changes only `tests/unit/test_exhaustive_research_unavailable_nas.py`, resolving each work item through candidate -> exact `source_id`, selecting the actual NAS item, and preserving unavailable-vs-irrelevant, processed=3, failed=0, 2/3 coverage and durable state assertions.
- Exact verification proves that repair is insufficient to close the remaining failure: Quality `34190083267` on `124bdd9d789230d33452cfbc2452b307d410316c` failed only full pytest; unchanged handoff descendant `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00` failed Quality `34190114472` only in full pytest; current unchanged diagnostic descendant `147d9527ff06ce772aa378e29befa00d77031e9e` failed Quality `34194199456` only in full pytest. On `34194199456`, Local install, Windows path safety, Linux storage, specification validator, Ruff and mypy all PASS.
- Root-cause boundary this run: the list-order/source-identity defect is CLOSED as the remaining primary cause. Three exact canonical pytest-only reds persist after that repair, including two unchanged descendants. The remaining failing assertion/traceback is still not exposed through the available GitHub connector: jobs expose the failing `Quality — pytest` step and successful diagnostics upload but not the diagnostics ZIP/log payload. Local direct reproduction is also blocked by transient DNS resolution of `github.com`.
- No speculative product-vs-harness patch is made without the exact remaining assertion. Next admissible progress is the exact pytest diagnostic or a concrete corrective successor that identifies the second defect.
- Integrator handoff: HOLD §72 until the second failure is exactly root-caused and a corrected exact successor is canonical green; do not weaken exact source identity, unavailable-vs-irrelevant, 2/3 coverage, persistence, Storage, Security, Recovery or Windows guards.

## ERR-0023 — Terminal Jobs action reason leaks implementation-oriented lifecycle wording

- Severity: P2.
- Status: `FIXED_PENDING_VERIFY`.
- Failing evidence: canonical Backend Quality `34177086068` on exact `076a0d1209fe1cb30c6cfe7f6735a39158036c28`; full pytest only failed at `tests/unit/test_pathena_jobs_lifecycle.py::test_action_availability_matches_durable_service_states[completed-enabled5]` because visible copy was `no lifecycle action is available`.
- Root cause: product copy in `src/athena/desktop/jobs_lifecycle.py::JobActionAvailability.reason()` exposed implementation-oriented wording; harness assertion valid.
- Minimal Error-owned fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`, terminal copy -> `This job is {state}; no actions are available.`.
- Develop integration: `568d57a63bb2253d97ca63e92b52e1df66505ac9`; current Develop `b5f824082fcd9d335ea55de76f88d23a3c0ee7e8` descends from that integration and retains the corrected terminal-copy class.
- Exact verification remains pending because no completed canonical Quality run is associated with the current Develop descendant specifically establishing the integrated Error wording. Equivalent UI green evidence is not substituted for exact Develop verification.

## Current worker evidence — 2026-09-08

- Spec/Core current `147d9527ff06ce772aa378e29befa00d77031e9e`: Quality `34194199456 = failure`, again pytest-only; all non-pytest canonical gates PASS. No new ERR allocated because this is the same unresolved `ERR-0024` lineage.
- Backend product `efdae09dc71a661ea5c81f67b8e2b09ac90c0080`: Quality `34195556143 = cancelled`; it was immediately superseded by handoff descendant `ea601b96d681580c2e8f1f1af40c7d97c347511e`, whose Quality `34195601115` is in progress. Cancellation alone is not treated as a product error.
- UI current `bcce837f347f8b67f3b4de1ab465f3e80c750eea`: Quality `34195898979` is in progress; no conclusion inferred.
- Develop `b5f824082fcd9d335ea55de76f88d23a3c0ee7e8` has no exact completed canonical Quality success establishing global promotion readiness.
- No exact-current evidence reproduced retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none reopened.

## Historical verified entries

- `ERR-0004` P2 FIXED — startup/readiness harness Ruff B010/I001; exact-green evidence retained.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift.
- `ERR-0020` P2 FIXED — exhaustive-research resume harness identity loss; verified green successor.
- `ERR-0021` FIXED — Jobs status-copy constructor-refresh monkeypatch leak; exact red-to-green successor.
- `ERR-0022` FIXED — Spec/Core Ruff import grouping; exact canonical green.
- All other prior FIXED entries retain their recorded evidence.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
