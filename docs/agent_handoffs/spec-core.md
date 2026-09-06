# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline inspected: `develop/pathena-next@da493c1390192425d50caddc451c1a497027027a`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains untouched.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization: `bca9f1ce8c72a894169cb049f954ab3cadef5517`, parents previous Core `daf618982b068557919b58a3e0e6935c9cf41afe` + Develop `da493c1390192425d50caddc451c1a497027027a`.

Required handoffs were inspected before mutation: `errors.md`, `backend.md`, `ui.md`, `integrator.md`. Active worker heads inspected: errors `118f3b2c182de43d1876c7c369a00282800018fa`, backend `7b37f0629d3a137301ef04284524a8dfd78c36d3`, ui `f09406daab9440ee77a06e907add84280b3ae936`. No `postmerge/integrator` ref exists; Integrator coordination remains through the versioned `docs/agent_handoffs/integrator.md` on Develop.

## Verified Core coverage retained

Normal-Hybrid Search facade/application wiring, contradiction gates, Research coverage/scoped modes, Historical Backfill and Local+Web authorization/candidate-freeze contracts remain integrated on Develop and were not reopened. No Archive/Protected scope or synthetic provenance was introduced.

## READY — Personal Memory exact-scope priority

Spec anchor: `docs/beta/06_Personal_Memory.md` §§14, 16, 23-26 and Scope Test §46.

Product/test commit: `fc89e430ab8e2576516754d6f246a49d455e2fca`.

Exact scoped Project/Workflow Memory is priority tier 0; global core collaboration preferences remain tier 1; other global Memory is tier 2 fallback. Deterministic within-tier ordering, lifecycle/sensitivity eligibility, protected-content fail-closed behavior, persistence and Human Control remain unchanged.

The initially triggered Quality run `34001002970` was cancelled after the branch advanced. Exact descendant `daf618982b068557919b58a3e0e6935c9cf41afe`, carrying byte-identical product/test content, completed canonical ATHENA Quality `34001080362` with conclusion `success`.

Integrator handoff: READY product `fc89e430ab8e2576516754d6f246a49d455e2fca`; exact green descendant `daf618982b068557919b58a3e0e6935c9cf41afe`; canonical Quality `34001080362=success`; current synchronized Core lineage begins at `bca9f1ce8c72a894169cb049f954ab3cadef5517`.

## Current follow-up — model-facing precedence acceptance

Beta §§14, 25-26 and Tests §§46-47 require the exact scope hierarchy to survive context composition, Memory to remain explicitly labeled `USER PREFERENCE`, and current-turn instructions to override stored preferences without mutating them.

Acceptance commit `91e511860c0a9346582f1077212cf247bdf2347d` adds `tests/unit/test_personal_memory_context_priority.py`. It composes real SQLite-backed `PersonalMemoryService.context_candidates()` into `ContextBuilderService` and asserts the model-facing order is exact scoped Memory, global core preference, global fallback; exact scope metadata remains present; all entries remain `USER PREFERENCE`; and the context policy retains `Current user message overrides USER PREFERENCE`.

This follow-up is `IMPLEMENTED / CANONICAL_PENDING`. No PASS is claimed until a real workflow run verifies this exact test lineage.

## Collision / runtime guards

The follow-up changes tests only. It does not modify UI, Storage, Provider/transport, packaging, pypdf metadata, frozen argv routing, Desktop/Worker process topology, DirectChat context budgeting, scheduler/lane-lock, migrations/storage-bootstrap, Research, Search, Claims/Evidence or PALLAS. Known Windows crash/runtime classes remain explicit Beta/release regression requirements and are not reopened without exact-SHA evidence.

## Next Alpha/Beta gap

First consume canonical verification for the model-facing Memory precedence acceptance. If green, hand the exact acceptance SHA to Integrator and immediately select the next highest evidence-backed bounded CHAT/KNOWLEDGE/RESEARCH/PALLAS/Provenance/Human-Control P0/P1/P2 gap. Do not manufacture a defect where production contracts already satisfy the Beta specification.
