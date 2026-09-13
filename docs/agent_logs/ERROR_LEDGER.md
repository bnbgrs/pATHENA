# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `8c2dda7794ef4949844feb30d265d34248aa4660` (`feat(core): integrate knowledge read API`). canonical Quality `34744264489 = IN_PROGRESS`; Linux Storage, Local Install/pypdf and Windows release guards are already SUCCESS, with Python full pytest still running at the latest check. Parent `f301540eb707013e7b88c08ef248ea98edc1564d` has canonical `34741552444 = SUCCESS`.
- Error worker before this update: `0d3fb6fc85f6d45f864166d8e758e5eb2a3d04c7`; zero workflow runs exist on `postmerge/errors`.
- Spec/Core: `bd5b0497a8c220e2a3a238f974109d060d7256e5`; Core Focused `34742250322 = SUCCESS`, canonical `34742250297 = SUCCESS`.
- Backend: `d23e8d841810e7551e38734948d3ee234314d761`; Storage Focused `34742857035 = FAILURE`, canonical `34742857005 = FAILURE`.
- UI: `8e0e27a430267dd266ab0d06b81376c4a3eddd4d`; UI Focused `34743903719 = FAILURE`, canonical `34743903695 = IN_PROGRESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0049`, `ERR-0053`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0052`.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none.

## ERR-0053 — current UI composer-square candidate fails exact UI Focused gate

- Severity: P2 integration blocker.
- Status: `OPEN`.
- Exact current reproducer: `postmerge/ui@8e0e27a430267dd266ab0d06b81376c4a3eddd4d`, UI Focused `34743903719 = FAILURE` in `Run exact changed UI tests plus navigation invariant`.
- Previous exact parent `718d9002d5300afce74b04b0e4e8d40a9d00642e` was UI Focused and canonical green.
- The one-commit delta from that green parent is bounded to `src/athena/desktop/pathena_design_tokens.py`, `src/athena/desktop/pathena_layout_refinement_2200.py`, and `tests/unit/test_pathena_layout_refinement_2200.py`; the added acceptance specifically requires `sendButton` to remain square at compact, comfortable and wide widths.
- canonical `34743903695` is still active. Its Specification Validator, Ruff, mypy, Linux Storage, Local Install/pypdf and Windows release-guard jobs are green so far; full pytest remains in progress.
- Do not guess the exact assertion from the red focused job. UI owns this bounded candidate and must consume its exact failing test output, apply the minimal presentation/test correction if needed, then rerun UI Focused and canonical. No Skip/XFail or navigation/test removal.

## ERR-0052 — Spec/Core Knowledge Read API Ruff/import blocker

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Former reproducer `postmerge/spec-core@3e3dc4d3f4777b083d9ef2b09819cbad51ab9034` had Ruff `I001` in `tests/unit/test_knowledge_read_api.py`.
- Current successor `bd5b0497a8c220e2a3a238f974109d060d7256e5` is exact green: Core Focused `34742250322 = SUCCESS`, canonical `34742250297 = SUCCESS`.
- Integrator imported only `src/athena/api/knowledge_read.py` and `tests/unit/test_knowledge_read_api.py` into Develop `8c2dda7794ef4949844feb30d265d34248aa4660`.
- Integrated canonical `34744264489` is still running. `FIXED` requires that exact Develop run to finish SUCCESS.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `OPEN`.
- Current Backend exact SHA `d23e8d841810e7551e38734948d3ee234314d761` remains red: Storage Focused `34742857035 = FAILURE`; canonical `34742857005 = FAILURE`.
- `d23e8d...` is a history-preserving sync descendant of prior reproducer `517ca6ebd98ee2ff719827b043e2eee7ddd1e2e1`; the sync adds no `src/athena/storage/**` or `tests/unit/test_storage*.py` changes. Therefore the current exact failure remains the same Storage-owned candidate, not a new Develop cascade.
- Storage Focused Ruff and mypy steps succeed; the candidate is rejected by the focused outcome enforcement after the invariant/changed-test phase. No evidence supports relaxing any sidecar identity guard.
- Required same-SHA promotion evidence remains: paired foreign WAL+SHM replacement rejected fail-closed; legitimate two-process startup succeeds; single-sidecar replacement and partial transitions remain rejected; legitimate complete publication/withdrawal behavior remains intact; Storage Focused and canonical both SUCCESS.
- Do not integrate the current Storage delta until those conditions hold.

## Persistent release guards

Closed historical signatures reopen only on a current exact-SHA reproduction. Current Develop `8c2dda...` has already passed Linux Storage, Local Install/pypdf and the Windows path/storage/durable-filesystem, packaged-runtime, adaptive 2048-context reserve and Core/API restart guard jobs while its full pytest continues. Current UI `8e0e27...` has likewise passed those non-pytest guard lanes. No persistent release-guard signature is reopened.

## CI discipline

- No competing canonical run was started by the Error worker.
- `postmerge/errors` had zero workflow runs before mutation.
- No foreign worker product branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail, guard weakening, or Security/Storage/Recovery relaxation occurred.
