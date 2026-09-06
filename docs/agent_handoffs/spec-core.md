# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline inspected: `develop/pathena-next@62aa4e9ff20919f32d5147d183521fbf98f49535`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains untouched.
- Worker branch: `postmerge/spec-core`.
- Previous worker head: `b9e8f18c83b25b2b3c6675ec9439b02393124457`.
- History-preserving NON-FORCE synchronization onto current Develop: `4fa0fcb4756ffd6b5c615bde3308201af1679491`, parents previous Core + current Develop.

Required handoffs were inspected before mutation: `errors.md`, `backend.md`, `ui.md`, `integrator.md`. Develop already integrates the Personal Memory exact-scope priority product/test slice; the model-facing cross-layer acceptance file was not yet present on Develop and was preserved on the synchronized Core worker.

## Verified Core coverage retained

Normal-Hybrid Search facade/application wiring, canonical Search DTO mapping, semantic-failure propagation, contradiction gates, Research coverage/scoped modes, Historical Backfill, Local+Web authorization/candidate-freeze and Personal Memory exact-scope priority remain verified/integrated. No Archive/Protected scope expansion or synthetic provenance was introduced.

## READY — model-facing Personal Memory scope precedence

Spec anchors: `docs/beta/06_Personal_Memory.md` §§14, 25-26 and Tests §§46-47.

Acceptance commit: `91e511860c0a9346582f1077212cf247bdf2347d`.
Exact green head: `b9e8f18c83b25b2b3c6675ec9439b02393124457`.
Canonical ATHENA Quality: `34003641444 = success`.
Synchronized current Core head carrying the identical acceptance blob: `4fa0fcb4756ffd6b5c615bde3308201af1679491`.

`tests/unit/test_personal_memory_context_priority.py` composes real SQLite-backed `PersonalMemoryService.context_candidates()` into `ContextBuilderService` and proves the model-facing `USER PREFERENCE` order remains exact scoped Memory, global core preference, global fallback; scope metadata remains exact; and the context policy preserves `Current user message overrides USER PREFERENCE` without mutating stored Memory.

Integrator handoff: READY for independent integration of the bounded acceptance test. No product behavior change is bundled in this follow-up.

## Runtime/release guards

This slice changes no packaging/provider/storage/runtime code. Windows pypdf metadata, fail-closed frozen argv routing, two-EXE process topology, bounded worker tree, adaptive 2048-context DirectChat guard, lane-lock/SchedulerLaneOwnership packaged-worker cluster, migration/storage-bootstrap signatures and the Beta/release crash regression matrix remain binding and were not reopened without exact-SHA evidence.

## Next Alpha/Beta gap

The next evidence-backed Personal Memory Core gap is automatic/model-inferred learning control from Beta §§10-13 and §§37-45. Current `src/athena/memory/` contains explicit command, models, repository and explicit-user service only; `PersonalMemoryService` states that no model is called in this slice, and no Review Queue/learning-control implementation is present in the module directory. The bounded next contract should begin with default `suggest`: a model-inferred non-sensitive preference must not become canonical Personal Memory directly; it must remain review-gated with model provenance, while sensitive inferred content must fail closed without explicit approval. Do not implement `auto_non_sensitive` or destructive merge semantics in the same first slice unless the current code/spec contracts justify them. Add focused persistence/provenance acceptance and canonical Quality before READY handoff.
