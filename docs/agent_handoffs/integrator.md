# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `96297a9e1780021f5a515072a2075fea6566900f`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `159fc680f6b883b60ed9b25a961c02afbd918ece`; spec-core `de62eb6a657b500f6abd2b1909ff1452c611572a`; backend `4495cab0492f0c70e6d0b5cbda1136c1d960ab86`; UI `90c4704d7ae5cad4c2fe15016ef1b0b73414d323`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, history rewrite, auto-merge or main promotion was used.

## Progress this run — adaptive DirectChat output reserve

No current worker was READY at mutation time. UI head `90c4704d7ae5cad4c2fe15016ef1b0b73414d323` had exact canonical Quality `34282327502` still pending, Backend remained in the v41/schema/WAL recovery chain, and Spec/Core remained dependency-held on Backend. The integrator therefore used the bounded cross-cutting rule on a current exact Develop release guard.

Current Develop still used a fixed 2048-token output reserve plus a 256-token safety margin. With a loaded LM Studio context of 2048 tokens, even a tiny prompt necessarily exceeded the preflight budget. The bounded fix keeps the configured reserve as an upper bound, computes the output actually available after persisted input and the safety margin, and reduces the effective reserve only when the loaded context requires it. If input plus safety margin leaves no token for output, DirectChat still fails closed with `ContextBuilderError`.

The effective reserve is recorded consistently in the model signature, ContextPackage budget and total-token estimate, so provenance reflects the generation budget actually authorized. No provider, Storage, Recovery, Security, scheduler/worker, packaging or Windows process behavior is changed.

Focused regression coverage is added in `tests/unit/test_direct_chat_context_budget.py`: a 2048-token loaded context with a small input receives an adaptive 1728-token reserve; a larger context preserves the configured 2048 reserve; and an exhausted input+safety budget remains fail-closed. No Skip/XFail or assertion weakening was added.

## Current quality/error state

- UI exact head `90c4704d7ae5cad4c2fe15016ef1b0b73414d323`: canonical Quality `34282327502` was pending when Develop mutation was prepared and was therefore not consumed as READY evidence.
- Backend head `4495cab0492f0c70e6d0b5cbda1136c1d960ab86` remains conservative hold while the current v41/schema/WAL error family is not exact-green.
- Error head `159fc680f6b883b60ed9b25a961c02afbd918ece` records current formatter/root-cause evidence; historical runtime signatures are not reopened without exact-current reproduction.
- Spec/Core head `de62eb6a657b500f6abd2b1909ff1452c611572a` remains dependency-held on Backend for the durable Delta chain.
- Exact Develop canonical Quality must be obtained for the integration commit before any further Develop mutation.

## Tracker / visual state

- `docs/development/ALPHA_BETA_PROGRESS.md` was read as current source of truth. No unsafe truncated whole-file rewrite was attempted; this DirectChat release-guard closure is recorded here until a safe targeted tracker update is available.
- The 11-screen manifest and Visual-Gap ledger remain evidence sources for UI work; this run has no visual/UI mutation and makes no new `MATCH` claim.
- Existing duplicate UI-GAP identifier history is not silently renumbered or overwritten.

## Next integration order

1. Do not mutate Develop while canonical Quality for this integration SHA is queued or in progress; first consume its exact result.
2. If UI `90c4704d7ae5cad4c2fe15016ef1b0b73414d323` obtains exact-head green Quality without superseding commits, review and integrate its bounded black/orange palette slice.
3. Keep Backend v41/schema/WAL prerequisites conservative; only unblock Spec/Core durable Delta after exact-green Backend evidence.
4. Preserve the remaining Windows/Packaging/Runtime regression matrix before any Beta/release claim.

## Persistent release guards

Retain explicit Beta/release acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
