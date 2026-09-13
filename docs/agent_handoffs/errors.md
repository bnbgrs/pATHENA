# pATHENA Error Handoff

## Baseline

- Develop: `8c2dda7794ef4949844feb30d265d34248aa4660`; canonical Quality `34744264489 = IN_PROGRESS`. Linux Storage, Local Install/pypdf and Windows release guards are already SUCCESS; Python full pytest is still running. Parent `f301540eb707013e7b88c08ef248ea98edc1564d` has canonical `34741552444 = SUCCESS`.
- Workers: Spec/Core `bd5b0497a8c220e2a3a238f974109d060d7256e5`; Backend `d23e8d841810e7551e38734948d3ee234314d761`; UI `8e0e27a430267dd266ab0d06b81376c4a3eddd4d`.
- Error worker entered this run at `0d3fb6fc85f6d45f864166d8e758e5eb2a3d04c7`; zero workflow runs existed on `postmerge/errors` before mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0049`, `ERR-0053`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0052`.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`.
- BLOCKED: none.

## ITERATION-1 — ERR-0052 owner-fixed and integrated

`ERR-0052 = FIXED_PENDING_VERIFY / P2`.

Current Spec/Core `bd5b0497a8c220e2a3a238f974109d060d7256e5` is exact green:

- Core Focused `34742250322 = SUCCESS`
- canonical `34742250297 = SUCCESS`

Integrator imported only `src/athena/api/knowledge_read.py` and `tests/unit/test_knowledge_read_api.py` into Develop `8c2dda7794ef4949844feb30d265d34248aa4660`. The integrated canonical run `34744264489` is active; no duplicate was started. Close to `FIXED` only if this exact Develop run completes SUCCESS.

## ITERATION-2 — ERR-0049 persists on current Backend descendant

`ERR-0049 = OPEN / P1`.

Current Backend `d23e8d841810e7551e38734948d3ee234314d761` is exact red:

- Storage Focused `34742857035 = FAILURE`
- canonical `34742857005 = FAILURE`

The current head is a history-preserving sync descendant of prior reproducer `517ca6ebd98ee2ff719827b043e2eee7ddd1e2e1`. The sync adds no Storage source or Storage-test mutations, so this remains the same Storage/Recovery root-cause cluster rather than a Develop cascade. Storage Focused Ruff and mypy succeed; the candidate still fails its focused outcome gate.

Do not integrate the Storage delta. Same-SHA promotion still requires legitimate two-process startup and fail-closed simultaneous foreign WAL+SHM replacement to pass together, while single/partial/publication/withdrawal invariants remain intact and Storage Focused + canonical both finish SUCCESS.

## ITERATION-3 — new ERR-0053 on current UI candidate

`ERR-0053 = OPEN / P2`.

Current UI `8e0e27a430267dd266ab0d06b81376c4a3eddd4d` has UI Focused `34743903719 = FAILURE` in the exact changed-tests/navigation step. Previous exact parent `718d9002d5300afce74b04b0e4e8d40a9d00642e` was UI Focused and canonical green.

The one-commit delta from that green parent is bounded to:

- `src/athena/desktop/pathena_design_tokens.py`
- `src/athena/desktop/pathena_layout_refinement_2200.py`
- `tests/unit/test_pathena_layout_refinement_2200.py`

The added acceptance requires `sendButton` to remain square across compact, comfortable and wide layout widths. The exact red workflow proves the candidate slice currently fails, but available GitHub metadata does not expose the individual failing assertion, so no narrower assertion is invented. UI must consume the exact test output and correct only the bounded presentation/test root cause.

UI canonical `34743903695` is still active. Its Specification Validator, Ruff, mypy, Linux Storage, Local Install/pypdf and Windows release-guard jobs are green so far; full pytest remains in progress.

## ITERATION-4 — current Develop candidate held under existing canonical

Develop `8c2dda7794ef4949844feb30d265d34248aa4660` already has canonical `34744264489` in progress. The run has passed Linux Storage, Local Install/pypdf and Windows release-guard jobs, while full pytest remains active. No duplicate canonical run was started and no Develop mutation was made by Errors.

## ITERATION-5 — release-guard/cascade classification

No persistent pypdf, Frozen argv, Desktop/Worker split, one-Desktop/bounded-worker, adaptive 2048 reserve, Windows lane-lock, duplicate-column, Core-startup or storage-bootstrap signature is currently reproduced on Develop or UI release-guard lanes. Backend's active red state remains Storage-owned `ERR-0049`; UI's new red state is the bounded candidate `ERR-0053`; Spec/Core `ERR-0052` is owner-green and integrated pending exact Develop closure.

## CI discipline

- No competing canonical run was started.
- `postmerge/errors` had zero workflow runs before mutation.
- No product code or foreign worker branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail, guard weakening, or Security/Storage/Recovery relaxation occurred.

## Integrator / worker handoff

- `ERR-0049 = OPEN / P1` -> Backend/Storage. Hold Storage delta until fail-closed paired-sidecar continuity and legitimate concurrent startup are both proven on one exact SHA.
- `ERR-0052 = FIXED_PENDING_VERIFY / P2` -> integrated on Develop `8c2dda...`; await canonical `34744264489`.
- `ERR-0053 = OPEN / P2` -> UI. Consume exact focused-test output for `8e0e27a...`; minimal bounded fix only, then UI Focused + canonical.

## NEXT_ROOT_CAUSE

1. Consume current Backend successor after `d23e8d...`; require same-SHA legitimate concurrent startup plus fail-closed paired foreign sidecar replacement.
2. Consume UI successor for `ERR-0053` and verify the bounded composer/layout candidate on exact UI Focused + canonical.
3. Consume Develop `34744264489`; if SUCCESS, close `ERR-0052`; open a new ID only for genuinely new exact-SHA failure evidence.
