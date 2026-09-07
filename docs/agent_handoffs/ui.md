# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@f2cc85c31769fb78adc01b56f8673fcae186595f`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `f7344aeace915c4f965320e4baaed31ed76ed5d3`.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Verified predecessor

`UI-GAP-0062` is exact-green and Integrator-ready.

- Product commit: `f82be0e672659ee74ce8aecae5a7b4f157cbe6a0`.
- Focused regression: `c37c8b17a5b33a68068c04c5b5b0fe41b53e927c`.
- Canonical ATHENA Quality Gate: `34124133923 = success` on exact head `8bd74b266028ccfac5b06d286f84d805261ac9e6`.
- Behavior: the cancellation-requested Jobs help keeps the durable `cancel_requested` state and action matrix unchanged while removing the raw persisted-state token from visible help text.

## Current bounded slice — UI-GAP-0063

Screen: `04 — Jobs`.
Category: Copy.
Status: `IMPLEMENTED_PENDING_VERIFY`.

Evidence: after UI-GAP-0062 removed the raw `cancel_requested` token, the same visible `JobActionAvailability.reason()` surface still described ordinary action availability using `persisted state ...` and terminal states using `lifecycle mutation`. Those phrases expose implementation/storage-domain terminology instead of product-facing Jobs help.

Product commit `50eb723d18430735b5dcbb246563ae8e863c62a9` changes only `JobActionAvailability.reason()` copy. Enabled actions now say the action is available while the job is in its real current state; disabled actions say unavailable; terminal states say no lifecycle action is available. Durable state normalization, transition availability, receipt parsing, scheduler/worker behavior, persistence, retries and cancellation semantics are unchanged.

Focused regression `1a92d020d565424da147909f137779f7ce1e35fc` preserves the complete durable-state availability matrix and requires projected help to exclude `persisted state` and `lifecycle mutation` while retaining the exact cancellation-requested human explanation and prohibiting the raw `cancel_requested` token. No Skip/XFail, Ruff relaxation or lifecycle assertion was weakened.

Canonical Quality must succeed on an exact final descendant carrying unchanged product/test blobs before Integrator promotion.

## Coordination

Before the new slice, the worker was synchronized with current Develop using two-parent history-preserving NON-FORCE merge `f7344aeace915c4f965320e4baaed31ed76ed5d3`. The merge kept the exact worker tree while recording current Develop as the second parent, because Develop's only two commits since the previous common base were the already-integrated Settings accessibility slice and its Integrator handoff. No Backend/Storage/Security semantics were authored by UI.

`docs/ui/VISUAL_GAP_LEDGER.md` now records `UI-GAP-0062` as FIXED with exact Quality evidence and registers `UI-GAP-0063` once as `IMPLEMENTED_PENDING_VERIFY`. The eleven-slot manifest remains exactly eleven entries and marks only Jobs as pending technical verification.

## Integrator handoff

READY now: `UI-GAP-0062`, product `f82be0e672659ee74ce8aecae5a7b4f157cbe6a0` + regression `c37c8b17a5b33a68068c04c5b5b0fe41b53e927c`, verified by canonical Quality `34124133923 = success` on exact head `8bd74b266028ccfac5b06d286f84d805261ac9e6`.

DO NOT integrate `UI-GAP-0063` until canonical Quality succeeds on an exact descendant carrying unchanged product `50eb723d18430735b5dcbb246563ae8e863c62a9` and focused regression `1a92d020d565424da147909f137779f7ce1e35fc`.

## Persistent release guards

Before Beta/release promotion, retain explicit regression acceptance for pypdf packaging metadata, frozen-child argv fail-closed routing, two-EXE Desktop/Worker split and bounded worker count, adaptive 2048-context DirectChat budgeting, the Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError` crash cluster, and storage-bootstrap/migration startup signatures. None is reopened here absent exact-current reproduction.