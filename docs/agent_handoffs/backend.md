# pATHENA Backend & Systems Handoff

## Baseline

- Integration base reviewed: `develop/pathena-next@606e9dc72278ec331856e998a1b3fb4fa4754787`.
- Worker branch: `postmerge/backend`.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.
- Worker and Develop are currently diverged from merge base `3cfef2c2ee67799066ceefaf9ea84287817f256a`; no force update/history rewrite is permitted.

## Verified Research UUID-container slice

Product/test commit `462fba22637e0083c87df32f987134ce0fb3de00` hardens `_stable_uuids()` so naked scalar text-like values and non-Sequence containers fail closed before Research actor/job/persistence side effects. Valid UUID sequence deduplication and deterministic byte-order sorting are unchanged.

Focused verifier run `33833496929` completed SUCCESS: install, focused pytest, Ruff, mypy and `git diff --check` all passed before the product/test commit was created. Temporary UUID verifier workflow was removed in cleanup commit `8d30cc4cc45f916a72007c1ba63f95da60e346ca`.

Canonical Quality run `33833527206` on the exact product SHA concluded `action_required` with no accepted PASS evidence; do not treat it as global green.

## Current backend slice — Research source-types container boundary

A new bounded gap is confirmed in `ResearchService.enqueue_local()`: `source_types` is annotated as `Sequence[SourceType]` but the runtime path previously accepted arbitrary iterable containers such as `set[SourceType]`. This can normalize and proceed to actor/job persistence rather than failing at the API boundary.

The bounded correction introduces `_stable_source_types(values: object)` with explicit Sequence narrowing, rejects scalar text-like/non-Sequence containers, preserves the existing per-element `SourceType` guard and deterministic `.value` sorting/deduplication, and routes `enqueue_local()` through that helper.

Temporary verifier workflow `.github/workflows/backend_research_source_types_boundaries.yml` is tooling-only. It must commit product/test files only after focused pytest, Ruff, mypy and diff-check all pass, and must then be removed before Integrator handoff.

## Retained invariants

- Research persistence, snapshot pinning and durable job creation semantics remain unchanged for valid inputs.
- ExternalAccessGateway authorization/audit/provenance/TOR/redirect/fsync/transactional Source behavior is untouched.
- No retries, cryptography, storage, recovery, Windows/Linux path or packaging behavior is changed.
- No skip/XFail, assertion weakening or guard weakening is allowed.

## Integrator handoff

- READY_FOR_BOUNDED_REVIEW: UUID product/test commit `462fba22637e0083c87df32f987134ce0fb3de00` has exact focused green evidence from run `33833496929`; independently separate it from tooling history before integration.
- NOT_READY: source-types boundary remains pending exact verifier completion and temporary workflow cleanup.

## Next backend slice

Consume the source-types verifier. If green, remove tooling, hand off its exact product/test SHA, then move to the next highest evidence-backed Research/Jobs/Storage/Recovery/Provider/Packaging gap. If red, fix only the exact diagnostic and rerun; do not weaken tests or runtime guards.
