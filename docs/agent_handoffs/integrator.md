# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `d5b4d1479416edd1cd55f8bff6190029f42d9289`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `36856ddf219895aacb58a3029c0f86736724caf6`; spec-core `25d3cf0a674086b3e8050bb730359674909288cc`; backend `55a6e95486c8b7501f27ed07748dc922803025ea`; UI `93367bc74dab77f8ffab65e7de538ee79fb5a72a`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, rebase, history rewrite, auto-merge or main promotion was used.

## Progress this run — UI-GAP-0016 unreadable local-settings identity

No current worker supplied a new READY slice: Spec/Core §74 exact product/test run `34226175559` was cancelled and its documentation descendant `34226233986` remained in progress; Backend application WAL composition run `34226701474` was cancelled; current UI run `34227608407` remained in progress. The hard progress rule therefore consumed the already exact-green deferred UI-GAP-0016 slice after an independent current-Develop review.

The verified worker product `b0bac270a461afdef3322550e6ddf3e49314653a` changes only Settings presentation identity on unreadable local per-model settings: `_read_model()` continues to use opaque `backend_model_id` for the storage group and persisted identity check, while the visible/accessibility error now receives and renders the selected model `display_name`. Exact UI head `f66a1cc2c80cf0cadc89ba1a4771345af79df934` passed canonical ATHENA Quality `33912482820 = success`.

Current Develop still contained the precise defect (`f"{model_id} · local settings unreadable"`) while already carrying the previously integrated fail-closed UI-GAP-0014/0015 freshness semantics. The bounded patch was applied as Develop commit `ae830c89bc4a1d122111bc50f5f07ab8aad58d1a`. The resulting product blob is `ca8a5f7e9af404ececdd1d3c14180e8852eeeea6`, byte-identical to the exact verified worker product blob, proving no unrelated product mutation was imported.

The worker focused test `5d819895dfbfecc6c7a24f46251d0e3a07791409` was reviewed but not transplanted because its file contains `pytest.importorskip("PySide6")`, which violates the Integrator no-Skip rule. Its exact-green canonical lineage remains supporting evidence; no Skip/XFail was introduced on Develop.

No persistence representation, QSettings storage-group identity, provider/Core behavior, network/security, Storage, Recovery, scheduler/worker, packaging or Windows-runtime semantics changed.

## Verification state

- Exact worker product: `b0bac270a461afdef3322550e6ddf3e49314653a`.
- Exact canonical verified descendant: `f66a1cc2c80cf0cadc89ba1a4771345af79df934` / Quality `33912482820 = success`.
- Develop integration: `ae830c89bc4a1d122111bc50f5f07ab8aad58d1a`.
- Resulting Develop product blob equals verified worker product blob: `ca8a5f7e9af404ececdd1d3c14180e8852eeeea6`.
- Local checkout/focused execution remained unavailable because local DNS could not resolve `github.com`; no fabricated local PASS is claimed.
- Exact-current-Develop canonical Quality is not yet available; no global-green or promotion-ready claim is made.

## Other worker state

- Error head `36856ddf219895aacb58a3029c0f86736724caf6`: shared pytest evidence remains handoff-only; historical crash signatures are not reopened absent exact-current reproduction.
- Spec/Core head `25d3cf0a674086b3e8050bb730359674909288cc`: §74 REDUCE-cancel acceptance remains not READY pending a successful exact canonical run.
- Backend head `55a6e95486c8b7501f27ed07748dc922803025ea`: application WAL scheduler composition remains not READY after exact product/test Quality cancellation.
- UI head `93367bc74dab77f8ffab65e7de538ee79fb5a72a`: current Quality `34227608407` remained in progress at review time.

## Alpha/Beta and UI state

- UI-GAP-0016 is integrated on Develop with exact-green worker evidence and byte-identical verified product content; tracker should move it from `IMPLEMENTED_PENDING_VERIFY` to `VERIFIED` once a safe non-destructive tracker edit is available.
- Original eleven reference images remain unavailable; all eleven screen slots remain `IMPLEMENTED_PENDING_VISUAL_REVIEW` and zero `MATCH` claims are made.
- No completion percentage is inferred.

## Next integration order

1. Obtain exact-current-Develop canonical Quality on the descendant carrying `ae830c89bc4a1d122111bc50f5f07ab8aad58d1a`.
2. Consume current Core/Backend/UI exact Quality results when completed and integrate exactly one compatible bounded READY successor.
3. If workers remain non-READY, independently review the next deferred exact-green Settings slice (`UI-GAP-0011`, `0012`, `0017`, `0018`, or `0020`) or actively unblock one collision-free worker slice.
4. Preserve the release crash-regression matrix before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
