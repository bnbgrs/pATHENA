# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop baseline for this run: `3421bee8f1ed00f1473a930b759cb7f272345d7e`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `000ea687f086f8ac3ffe25cce144db4402d0edca`; spec-core `06b121edfcc80d0a9e50ffa4173baaea8060d3f9`; backend `e3c96cbdb2b04b90179bcc743ccaf20c6f26b837`; UI `2b54226815b0bb3b49832f1d64f1ac5b46716d41`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update, history rewrite, auto-merge or main promotion was used.

## Exact evidence consumed

- Current Develop product/test tree had no exact-head check run when mutation eligibility was checked.
- Spec/Core `06b121edfcc80d0a9e50ffa4173baaea8060d3f9` carries current Develop as second parent and differs from Develop only in `docs/agent_handoffs/spec-core.md`; canonical Quality `34285298078` completed SUCCESS. This independently verifies the adaptive DirectChat product/test tree already present on Develop.
- Backend `e3c96cbdb2b04b90179bcc743ccaf20c6f26b837` canonical Quality `34286119711` completed FAILURE; Backend v41/schema/WAL remains non-READY.
- UI `2b54226815b0bb3b49832f1d64f1ac5b46716d41` canonical Quality `34287102867` was pending and therefore not consumed as READY evidence.

## Progress this run — DirectChat boundary regression

No new compatible product worker was READY. A bounded Core-owned release-guard regression was added for the adaptive output reserve boundary: with a 2048-token loaded context, 1791 estimated input tokens and a 256-token safety margin, exactly one output token remains and must be preserved. At 1792 input tokens the existing fail-closed regression still requires `ContextBuilderError`.

This locks the off-by-one boundary around the known 2048-context failure class without changing production behavior, provider contracts, Storage, Recovery, Security, scheduler/worker, packaging or Windows process semantics. No Skip/XFail or assertion weakening was added.

## Current quality/error state

- Adaptive DirectChat product tree: independently canonical-green via Spec/Core Quality `34285298078` before this added boundary-only regression.
- Backend remains conservative hold while its exact current Quality is red.
- UI current exact Quality was still pending at review time.
- Historical runtime signatures remain release guards and are not reopened without exact-current reproduction.

## Tracker / visual state

- `docs/development/ALPHA_BETA_PROGRESS.md`, current handoffs, 11-screen manifest and Visual-Gap ledger remain source-of-truth inputs; no percentage or new visual `MATCH` claim is introduced here.
- No UI product mutation was made in this run.

## Next integration order

1. Re-check exact-current Develop Quality before any further Develop mutation.
2. Consume the completed exact UI head Quality and integrate only if it is non-superseded, bounded and compatible.
3. Keep Backend v41/schema/WAL prerequisites conservative until exact-green; only then unblock dependent Core composition.
4. Preserve the Windows/Packaging/Runtime regression matrix before any Beta/release claim.

## Persistent release guards

Retain explicit Beta/release acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting including the one-token boundary; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
