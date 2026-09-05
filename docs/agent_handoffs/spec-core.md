# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline inspected: `develop/pathena-next@fdbf882eede84bfcc5debc6cfffc311fdfb1e440`.
- Worker branch: `postmerge/spec-core`.
- Exact verified product/test head: `dd7d23672ecf634d3bda4ed466df3c596b792f67`.
- Canonical Quality: `33944149694 = success` on that exact head.
- History-preserving NON-FORCE synchronization onto the inspected Develop baseline: `451772e57f0edfd38a2fce95ec10a882473c1275`, parents `dd7d23672ecf634d3bda4ed466df3c596b792f67` and `fdbf882eede84bfcc5debc6cfffc311fdfb1e440`.
- `main` and `bnbgrs/ATHENA` were not mutated.

## Spec anchors

Primary anchors: Beta Knowledge/Claims §§56, 58-60 and tests §§69-70 in `docs/beta/05_Wissenseinheiten_Claims_und_Wissensgraph.md`.

The contract requires contradiction detection to produce candidates first, account for temporal validity before contradiction marking, avoid treating different sources' attributed opinions as automatic objective contradictions, retain historical Claims, and preserve explicit human review authority.

## READY — production acceptance combined contradiction gate

Status: `VERIFIED_ON_WORKER / READY_FOR_INTEGRATOR_REVIEW`.

The verified lineage composes the exact canonical left/right Claim revisions through the deterministic temporal and attribution gate before durable contradiction-review creation in the real `ProposalAcceptanceService.accept_all()` production path.

Verified product behavior:

- exact entity/revision identity is retained from canonical deduplication through review enqueue;
- review candidacy requires both temporal and attribution policies to permit it;
- provably disjoint temporal windows create no contradiction review;
- two `ATTRIBUTED_OPINION` Claims attributed to distinct real persisted entities create no contradiction review;
- no attribution identity, Source/Evidence provenance, or PALLAS data is synthesized;
- permitted candidates retain processing-run/model/entity/revision/confidence/reason/timestamp metadata;
- existing `ReviewService` deduplication and explicit human accept/reject semantics remain unchanged;
- missing exact revisions remain fail-closed.

The SQLite production regression uses two real persisted speaker Knowledge entities as `attributed_to_entity_id` foreign-key targets and asserts both empty returned contradiction-review IDs and zero persisted contradiction review rows. The earlier synthetic UUID fixture failure was corrected without weakening product behavior or assertions.

## Verified files carried by synchronization

- `src/athena/knowledge/acceptance_service.py` — blob `28fa197acc39f09a28fda437ba18718cb5095e99`.
- `src/athena/knowledge/contradiction_review_enqueue.py` — blob `cf4ef39af54436c23e2f5fb69ad58c0ed261ba1f`.
- `tests/unit/test_contradiction_review_enqueue.py` — blob `e07f88947cf23e8a295e5ff7846d98613fae36cd`.
- `tests/unit/test_proposal_acceptance_attribution_gate.py` — blob `43052124548923ef947c9a347d604e5f5fc0bcb1`.

## Integrator handoff

Integrator may independently review and consume exact-green Core head `dd7d23672ecf634d3bda4ed466df3c596b792f67`, canonical Quality `33944149694 = success`. Synchronization commit `451772e57f0edfd38a2fce95ec10a882473c1275` only rebases the verified Core-owned blobs onto the inspected current Develop tree by a two-parent history-preserving merge; it does not weaken or expand the verified contract.

## Collision avoidance

Backend-owned storage/runtime/recovery/transport work was not modified. UI/Qt presentation work was not modified. Error-worker findings were inspected and no new stable Core-owned error signature was adopted. PALLAS was not populated with synthetic data.

## Next Core gap

Direct code tracing of `ChatKnowledgeExtractionService` found no contradiction-review persistence bypass; extraction performs model-side pair classification but does not itself persist semantic review items. The next candidate remains evidence-driven: inspect remaining production knowledge composition paths for any direct `ReviewService.enqueue_contradiction()` call that bypasses `enqueue_canonical_contradiction_review()`. If none exists, proceed to the outstanding bounded Research repository-finalization source-coverage composition recorded in `docs/development/ALPHA_BETA_PROGRESS.md`, using a complete-blob deterministic mutation path because `repository.py` is large. Do not re-describe the earlier large-file tooling blocker without attempting the complete-blob path.
