# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline used for this run: `develop/pathena-next@4d36d5f13e1449973e74c48df5e2efb53d0e8aae`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization: `1be7e1edbd7f084eab4da7da87f7c6f973d331d8`, retaining the previously verified contradiction-gate product/test blobs while taking current Develop as second parent.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Verified prior Core slices

- Normal Hybrid Search `HybridRetrievalService -> AthenaApplication -> CoreApiFacade -> search.normal.hybrid`: verified and integrated into Develop.
- `TemporalContradictionPolicy`: verified and integrated into Develop.
- Exact canonical revision adapter `assess_canonical_claim_revisions()`: product `214e0dc3ff8d7227bae023d7f368ebfa62daa779`, tests `b3a87154fda34c9d9044d0bb1f2f58d4e37471f5`, exact Quality run `33812392688 = success`.

## Current product slice — ProposalAcceptanceService temporal contradiction gate

Spec anchor: `docs/beta/05_Wissenseinheiten_Claims_und_Wissensgraph.md`, especially the temporal contradiction requirements around §§56, 58, 60 and 69-70.

Product commit: `11b56867dd2f23d7149bc9defa299434e3ca5409`.
Focused acceptance-test commit: `209c5c3715c8e560e0c3954c3cd88991876f9086`.

`ProposalAcceptanceService.accept_all()` now evaluates the exact left/right canonical revision IDs immediately before the existing contradiction-review enqueue, using the same SQLite write-transaction connection. Only a verified temporal assessment with `permits_contradiction_candidate == False` suppresses enqueue. Overlapping, touching, open and unknown periods retain the existing explicit human-review path. Missing/non-Claim exact revisions still fail closed through the already verified adapter; no exception swallowing or synthetic temporal inference was added.

The composition does not create a contradiction relation, does not infer timestamps, does not substitute mutable current heads for the exact review revisions, and does not alter storage schema, security, recovery, provider/transport or UI behavior.

## Acceptance evidence

`tests/unit/test_proposal_acceptance.py` now adds a focused composition case that persists two real canonical Claim revisions with disjoint validity windows, routes the proposal through canonical-reuse decisions, and verifies that no contradiction semantic-review item is created. The pre-existing acceptance test still requires the unknown-window path to enqueue a contradiction review, protecting the fail-closed human-review behavior.

The test uses real persisted Claim revisions and the real temporal gate/review storage path. Deduplication planning is fixed to the intended canonical-reuse decisions only to isolate the composition boundary; the temporal assessment itself is not mocked.

Canonical Quality run `33825883574` was created for exact product/test head `209c5c3715c8e560e0c3954c3cd88991876f9086`; at handoff-update time it remained pending behind an older full-pytest Core run. No PASS is claimed for the new slice until a run containing the current product/test delta completes successfully.

## Ownership / collision avoidance

- No Backend, Storage, Security, Provider/Transport or UI product files were changed.
- Error-worker ownership remains independent; no new confirmed Core error ID is allocated here.
- PALLAS is untouched; no simulated/fake Source, Claim, Knowledge or Research data was introduced.

## Integrator handoff

Status: `NOT_READY_PENDING_CANONICAL_QUALITY`.

Review bounded commits `11b56867dd2f23d7149bc9defa299434e3ca5409` and `209c5c3715c8e560e0c3954c3cd88991876f9086`. Integrate only after canonical Quality on a head containing both commits completes green. Do not merge the draft worker PR automatically and do not promote to main.

## Next Alpha/Beta gap

After green verification, hand this bounded acceptance-gate slice to Integrator and select the highest unclaimed P0/P1/P2 Core gap from current Alpha/Beta coverage. Prefer a small real CHAT/KNOWLEDGE/RESEARCH/PALLAS composition gap; do not expand temporal extraction semantics unless the specs and current contracts establish a grounded source for validity timestamps.
