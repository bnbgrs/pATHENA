# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline inspected: `develop/pathena-next@ff780f2edf367320340771ffc3176d9fc1724c5c`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains untouched.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization: `6b1e48d8cc9dad7971b367e1591734d98b5e03aa`, parents previous Core `0166f4dbc6962fe8fd1f96de2d265d6767b009dc` + Develop `ff780f2edf367320340771ffc3176d9fc1724c5c`.

Required handoffs were inspected before mutation: `errors.md`, `backend.md`, `ui.md`, `integrator.md`. Active worker heads inspected: errors `0017b4d83481ba46e020d12492eb5c1d0a5fca7a`, backend `02707d295e31e8d321ba6f2ed1bd6f50197eeb81`, ui `1d82f95268affd9fd700e1b3079120887760f97b`.

## Previously verified Core coverage retained

Normal-Hybrid Search facade/application wiring and established Research/Local+Web slices remain integrated on Develop and were not reopened. No Archive/Protected scope or synthetic provenance was introduced.

## Current product slice — Personal Memory scope priority

Spec anchor: `docs/beta/06_Personal_Memory.md`, especially §§14, 16, 23-26 and Scope Test §46.

Beta requires:

`explicit current user instruction > specific Project/Workflow Memory > global Memory > default configuration`.

The current `PersonalMemoryService.context_candidates()` implementation contradicted this hierarchy: global core preferences were tier 0 while exact scoped Memory was tier 1. Existing `tests/unit/test_personal_memory.py` encoded the same reversed order by requiring the global core preference at candidate index 0.

Product/test commit: `fc89e430ab8e2576516754d6f246a49d455e2fca`.

The bounded correction:

- makes exact current-scope Memory tier 0;
- keeps global core collaboration preferences eligible everywhere as tier 1;
- keeps other global Memory as tier 2 fallback;
- preserves deterministic within-tier ordering by newest revision then stable `memory_id`;
- preserves eligibility, lifecycle, sensitivity/protected fail-closed behavior and persistence semantics;
- does not mutate current-turn instructions or automatically rewrite Memory.

Acceptance now proves, for an exact Project scope, ordering is exact scoped Memory first, global core preference second, other global fallback third, while another Project's Memory is excluded. Global-only retrieval remains core preference before other global fallback.

Files changed only:

- `src/athena/memory/service.py`
- `tests/unit/test_personal_memory.py`

No packaging, frozen argv routing, Desktop/Worker process topology, DirectChat context budgeting, lane-lock/scheduler, migration/storage-bootstrap or Windows release guards were changed.

## Verification state

Canonical ATHENA Quality run `34001002970` was triggered on exact product/test SHA `fc89e430ab8e2576516754d6f246a49d455e2fca` through PR #56. At handoff write time it is `pending` and has not exposed runnable jobs yet.

Therefore this slice is `IMPLEMENTED / CANONICAL_PENDING`, not READY. No PASS is claimed without the real run.

## Integrator handoff

Do not integrate the Personal Memory priority slice until exact canonical Quality `34001002970` (or an exact descendant carrying the same two product/test blobs) completes successfully. If green, version the exact READY evidence and hand `fc89e430ab8e2576516754d6f246a49d455e2fca` to Integrator. If red, fix only the smallest concrete root cause; do not weaken scope precedence, eligibility, lifecycle, protected-content or Human-Control assertions.

## Next Alpha/Beta gap

First consume canonical Quality `34001002970`. If green, immediately select the next highest evidence-backed bounded CHAT/KNOWLEDGE/RESEARCH/PALLAS/Provenance/Human-Control P0/P1/P2 gap from current Develop/Alpha-Beta coverage. Preserve all verified Normal-Hybrid Search and Research contracts and keep PALLAS data-driven only.

## Release guards retained

Known Windows pypdf packaging metadata, fail-closed frozen child argv routing, two-EXE topology, bounded/non-growing worker tree, adaptive DirectChat 2048-context reserve/safety behavior, lane-lock/scheduler packaged-worker crash cluster, duplicate-column and storage-bootstrap startup signatures remain explicit Beta/release regression requirements. None are reopened without exact-SHA evidence, and no promotion-ready claim is made while any known reproduced crash signature remains open.
