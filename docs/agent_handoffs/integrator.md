# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `20619f1310bef9d7d2aa706cff11a974144c47e5`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `cdf10f83e43567ed2d3f7b2d2162e5aa7c6a6509`; spec-core `f4abb89d7538a11efa50d94a847b6f69139c602b`; backend `aa9cb18188bf070ac4b9f0e2763e2b31c643a54f`; UI `b9936b6e404c224c47230ced5919f475760c013a`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, rebase, history rewrite, auto-merge or main promotion was used.

## Progress this run — Exhaustive Research §73 external capture acceptance

Spec/Core §73 became READY during this run. Exact worker commit `bb5806123097171598584166ff10f3b5e28d07ca` completed canonical ATHENA Quality `34219791632 = success`. The bounded slice is test-only, contains no Skip/XFail or weakened assertion, and adds one real orchestration acceptance proving external evidence is durably captured and pinned before Research consumes it.

Independent Develop review confirmed `tests/unit/test_exhaustive_research_external_capture.py` was absent and that Develop-only changes since the worker's reconciled baseline were disjoint Settings/integrator changes. The exact verified test contents were integrated on Develop as commit `4dcf7eb9366a4323fa0bd199014068938cd64294`.

The acceptance uses a real `AthenaApplication`, real `ExternalAccessGateway`, real durable `WEB_SNAPSHOT` capture, real provenance rows, and real Local+Web Research candidate freezing. It locks exactly one external transport fetch at capture time, immutable Source/blob identity and SHA across Research use, and zero re-fetches during candidate/source resolution.

No production, Search, Storage, WAL, Security, Recovery, scheduler/worker, provider/transport, packaging or Windows-runtime semantics changed.

## Verification state

- Exact §73 worker commit: `bb5806123097171598584166ff10f3b5e28d07ca`.
- Exact canonical Quality: `34219791632 = success`.
- Validator, Ruff, mypy, Local install smoke, Linux storage regressions, Windows path safety and canonical pytest all completed successfully in that exact run.
- Develop integration commit: `4dcf7eb9366a4323fa0bd199014068938cd64294`.
- Exact-current-Develop canonical Quality is not yet available; no global-green or promotion-ready claim is made.
- No Skip/XFail, assertion weakening or guard relaxation was introduced.

## Other worker state

- Error head `cdf10f83e43567ed2d3f7b2d2162e5aa7c6a6509`: `ERR-0025` remains IN_PROGRESS and `ERR-0023` remains FIXED_PENDING_VERIFY; repeated worker pytest-only reds remain deduplicated until an exact assertion is exposed.
- Backend head `aa9cb18188bf070ac4b9f0e2763e2b31c643a54f`: current canonical WAL runtime-boundary Quality `34221259239` is pending and is not READY.
- UI head `b9936b6e404c224c47230ced5919f475760c013a`: synchronized worker lineage is not consumed this run because §73 is the single bounded progress slice.
- Spec/Core head `f4abb89d7538a11efa50d94a847b6f69139c602b`: documentation descendant of the integrated §73 test; §74 Cancel Test is the next Core gap.

## Alpha/Beta and UI state

- Exhaustive Research §73 external capture acceptance is integrated with exact-green evidence and should be tracked as `VERIFIED`.
- The original eleven reference images remain unavailable; all eleven screen slots remain implemented pending visual review and zero `MATCH` claims are made.
- No completion percentage is inferred.

## Next integration order

1. Obtain exact-current-Develop canonical Quality on the descendant carrying `4dcf7eb9366a4323fa0bd199014068938cd64294`; close `ERR-0023` only on exact-green Develop evidence.
2. Consume Backend `34221259239` and the current UI exact Quality when completed; integrate exactly one compatible bounded READY successor.
3. If workers remain non-READY, implement or unblock exactly one small unclaimed cross-cutting gap; Core §74 Cancel Test is the current Spec/Core successor.
4. Preserve the release crash-regression matrix before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
