# pATHENA Backend & Systems Handoff

## Baseline

- Integration base reviewed: `develop/pathena-next@606e9dc72278ec331856e998a1b3fb4fa4754787`.
- Worker branch: `postmerge/backend`.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.
- Worker and Develop are diverged from merge base `3cfef2c2ee67799066ceefaf9ea84287817f256a`; no force update/history rewrite is permitted.

## Verified Research UUID-container slice

Product/test commit `462fba22637e0083c87df32f987134ce0fb3de00` hardens `_stable_uuids()` so naked scalar text-like values and non-Sequence containers fail closed before Research actor/job/persistence side effects. Valid UUID sequence deduplication and deterministic byte-order sorting are unchanged.

Focused verifier run `33833496929` completed SUCCESS: install, focused pytest, Ruff, mypy and `git diff --check` all passed before the product/test commit was created. The temporary UUID verifier was removed in cleanup commit `8d30cc4cc45f916a72007c1ba63f95da60e346ca`.

Canonical Quality run `33833527206` on the exact product SHA concluded `action_required`; it is not global PASS evidence.

## Next confirmed backend gap — Research source-types container boundary

`ResearchService.enqueue_local()` annotates `source_types` as `Sequence[SourceType]`, but the current runtime path accepts arbitrary iterable containers such as `set[SourceType]`: every element passes the existing element guard and normalization can continue into actor/job persistence. The required bounded fix is an explicit Sequence/container guard before normalization while retaining the existing per-element `SourceType` guard and deterministic `.value` sort/dedupe behavior.

A temporary GitHub verifier was created to apply and test this exact patch, but pushes containing the newly created workflow produced no workflow run. No product/test mutation from that verifier was committed, and the temporary workflow was removed again in `e7a205197573c78a87edb0ed33fb0cf984fbbd74`. This is a first-cycle tooling blocker only; it must not be repeated unchanged next run. Use direct Git-data mutation with complete current blobs or another safe disjoint Backend slice if exact verified mutation cannot be produced.

## Retained invariants

- Research persistence, snapshot pinning and durable job creation semantics remain unchanged for valid inputs.
- ExternalAccessGateway authorization/audit/provenance/TOR/redirect/fsync/transactional Source behavior is untouched.
- No retries, cryptography, storage, recovery, Windows/Linux path or packaging behavior changed.
- No skip/XFail, assertion weakening or guard weakening.

## Integrator handoff

READY_FOR_BOUNDED_REVIEW: UUID product/test commit `462fba22637e0083c87df32f987134ce0fb3de00` with exact focused green evidence from run `33833496929`. Independently isolate product/test content from tooling history before integration. Canonical global PASS is not claimed.

## Next backend slice

Apply and verify the confirmed `source_types` Sequence boundary through direct Git-data/full-blob mutation or another executable safe path. If that cannot be done without reconstructing a truncated large file, implement one disjoint evidence-backed Backend/System slice instead of repeating the workflow blocker.
