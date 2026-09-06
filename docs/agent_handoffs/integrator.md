# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `fd15a75212acac7f88886117835b8d754577ea91`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `2b42d3acfc11cf3862659e272ff920cd43f77873`; spec-core `b4d7ac9d0102981b133983c5fa93e113e2df4360`; backend `20edbed46471a50e72661e2e69502b094a0b599f`; ui `5a40e75ed78293ddd8c1ea3533c5632d6dea2910`.
- `main` and `bnbgrs/ATHENA` were untouched.

## Integrated this run — Local provider bounded-read/type boundaries

READY Backend lineage independently reviewed:

- bounded read-size true-int validation product `e6ae4998b675d8ed83efc266fd7d73063e1df63c`;
- finite/remaining-aware regression harness correction `5abee1fb3cf9aa639a2600796036302ef63a773d`, closing ERR-0015 without weakening the `remaining + 1` overflow probe;
- local response-body runtime bytes boundary product `2a535bf6d9b1adebfb6a48a27451c72bd9625fba` plus focused regression `2fa14059823873aa249fc2bc3999cd65994ae626`;
- exact-green Backend successor `9dc8375399c6b07f9c52545783004607aa9dd430`, canonical Quality `34011613102 = success`.

The exact verified `src/athena/model/adapters/local_http.py` blob plus the two focused regression files were transplanted onto exact current Develop without importing Backend history or unrelated handoff/doc changes.

Develop integration commit: `42a3d619c3e6fb8f6721b983a7ed7a579e84c915`.

## Contract now covered

`_BoundedLocalResponse.read()` rejects bool/non-int explicit sizes before delegate I/O; valid negative integer reads retain bounded remaining+1 overflow detection. `read()` and `readline()` now fail closed on non-`bytes` response bodies before byte accounting. Existing loopback-only/proxy-free routing, redirect rejection, total-deadline bounds, byte caps, provider behavior, Storage/Security/Recovery/audit/provenance and Windows runtime invariants remain unchanged.

## Validation state

- Exact worker lineage passed canonical Quality `34011613102 = success`.
- ERR-0015 is closed in the Error handoff with verified harness correction and canonical Quality `34009044381 = success`.
- Independent Develop compare confirms exactly three files changed: `src/athena/model/adapters/local_http.py` (+11/-3), `tests/unit/test_local_http_read_size_validation.py` (+48), and `tests/unit/test_local_http_response_type_validation.py` (+46).
- No pull-request-triggered workflow run is currently associated with the exact Develop integration SHA; repository-wide green is therefore not claimed for that SHA.

## Other current inputs

- UI-GAP-0033 is READY under exact documentation head `644c3cd5e3fd9c646b5e9d881a821b25d55b70ea`, Quality `34012079406 = success`, but was deferred by the single-bounded-slice rule.
- UI-GAP-0034 remains pending exact canonical verification.
- Core reviewed-inference acceptance remains pending canonical Quality; no READY claim is consumed.
- Backend bounded response constructor limits remain NOT READY while Quality `34014086876` is pending.
- Eleven UI screens remain implemented pending visual review; pixel-level MATCH remains unclaimed.

## Runtime/release guards retained

Known Windows pypdf packaging, fail-closed frozen argv routing, bounded process tree, adaptive 2048-context DirectChat budgeting, lane-lock/SchedulerLaneOwnership packaged-worker crash cluster and storage-bootstrap/migration startup signatures remain explicit Beta/release regression requirements. This Backend slice does not alter their owning semantics.

## Next integration order

1. Prefer any newer exact-green bounded Core composition successor after independent compatibility review.
2. Otherwise consume exactly one compatible READY successor; UI-GAP-0033 is currently eligible.
3. Do not integrate Backend bounded response constructor limits until exact canonical Quality succeeds.
4. Obtain exact-current-Develop Quality before repository-wide green or promotion-ready claims.
5. Before Beta/release readiness, explicitly regress all retained Windows packaging/process-tree/startup/chat-context/lane-lock crash classes on the exact candidate SHA.

## Rules retained

- No direct work on `main`; no main promotion.
- No force-push, history rewrite or auto-merge.
- No Skip/XFail, weaker assertions, Security/Storage/Windows/Recovery/validator relaxation, fake success or fabricated provenance.
