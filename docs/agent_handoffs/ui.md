# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@15f4a439d15d4bb1414e7b54afee7a25ced36e61`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `944f933fdbfe9e4e631c21f538ef17ac722f2940`.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Verified predecessor

`UI-GAP-0061` is exact-green and Integrator-ready.

- Product commit: `ffac0e737c3c3457a49ce4b830492f26ba7127d1`.
- Focused regression: `930dc168f5700f03720601664caf23b08ecd7603`.
- Canonical ATHENA Quality Gate: `34118404763 = success` on exact head `8454d633810283e47d0b9bb9b93321536440cb45`.
- Behavior: existing Settings help tooltips are mirrored into `accessibleDescription`; model/provider selection, context budgeting, output limits, sampling, reasoning state and persistence are unchanged.

## Current bounded slice — UI-GAP-0062

Screen: `04 — Jobs`.
Category: Copy.
Status: `IMPLEMENTED_PENDING_VERIFY`.

Evidence: `JobActionAvailability.reason()` exposed the internal persisted-state token `cancel_requested` directly in visible Jobs action-help copy after cancellation had already been persisted. The lifecycle state itself is valid and must remain unchanged; the UI projection should explain it in product language rather than leak an underscore-delimited implementation token.

Product commit `f82be0e672659ee74ce8aecae5a7b4f157cbe6a0` changes only that already-cancel-requested help string to `Cancellation has already been requested and is waiting for worker acknowledgement.` It does not change durable job state, transition availability, receipt parsing, scheduler/worker behavior, persistence, retries or cancellation semantics.

Focused regression `c37c8b17a5b33a68068c04c5b5b0fe41b53e927c` preserves the full durable-state availability matrix and additionally requires the human cancellation explanation while prohibiting the raw `cancel_requested` token in the projected help text. No Skip/XFail, Ruff relaxation or lifecycle assertion was weakened.

Canonical ATHENA Quality Gate `34124016008` is pending on exact product/test head `c37c8b17a5b33a68068c04c5b5b0fe41b53e927c`. Documentation successors carry unchanged product/test blobs and will require exact final-lineage Quality before Integrator promotion.

## Coordination

The worker was synchronized with current Develop using a two-parent history-preserving NON-FORCE merge. Current Develop's `docs/agent_handoffs/integrator.md`, `src/athena/desktop/pathena_startup_experience_2900.py`, and `tests/unit/test_pathena_startup_experience_2900.py` were preserved from Develop while the verified Settings slice remained intact. No Backend/Storage/Security semantics were authored by UI.

`docs/ui/VISUAL_GAP_LEDGER.md` records `UI-GAP-0061` as FIXED with exact Quality evidence and registers `UI-GAP-0062` once as `IMPLEMENTED_PENDING_VERIFY`. The eleven-slot manifest remains exactly eleven entries and marks only Jobs as pending technical verification.

## Integrator handoff

READY now: `UI-GAP-0061`, product `ffac0e737c3c3457a49ce4b830492f26ba7127d1` + regression `930dc168f5700f03720601664caf23b08ecd7603`, verified by canonical Quality `34118404763 = success` on exact head `8454d633810283e47d0b9bb9b93321536440cb45`.

DO NOT integrate `UI-GAP-0062` until canonical Quality succeeds on an exact descendant carrying unchanged product `f82be0e672659ee74ce8aecae5a7b4f157cbe6a0` and focused regression `c37c8b17a5b33a68068c04c5b5b0fe41b53e927c`.

## Persistent release guards

Before Beta/release promotion, retain explicit regression acceptance for pypdf packaging metadata, frozen-child argv fail-closed routing, two-EXE Desktop/Worker split and bounded worker count, adaptive 2048-context DirectChat budgeting, the Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError` crash cluster, and storage-bootstrap/migration startup signatures. None is reopened here absent exact-current reproduction.
