# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@25089e434412e7c1b8ede229438324338a0d5da0`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Worker synchronized history-preservingly and NON-FORCE through merge `26dd9696d8d3cfe3b405415682f2218e4fd9f52b`, preserving current Develop plus the verified combined contradiction-gate product/test blobs.
- Active worker heads observed before mutation: backend `d507de617f27976b174c1beadb22d8432fef63d6`, errors `853bec9df7bdaa676ebc2424cbdc7b7bfb628f3a`, ui `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.

## Verified predecessor — exact-revision combined contradiction gate

- Product: `b10bdc52eba9449a105a0db57466771ad4412a63`.
- Focused tests: `8eab1e513a5957a01e1c3e2afcdeaa885965de96`.
- Ruff-only semantic-no-op fix: `b1da19a0aab5a80bc9cef06ff68cf92dfdb61317`.
- Canonical ATHENA Quality: `33925078295 = success` on exact head `b1da19a0aab5a80bc9cef06ff68cf92dfdb61317`.
- Status: `VERIFIED_ON_WORKER / READY_FOR_INTEGRATOR_REVIEW`.

The exact immutable left/right Claim revisions are loaded once and assessed by both temporal and attribution policies. `permits_contradiction_candidate` is true only when both policies permit candidacy. Missing revisions fail closed; no identity, provenance or PALLAS state is synthesized.

## Current product slice — contradiction-review persistence composition

Spec anchor: `docs/beta/05_Wissenseinheiten_Claims_und_Wissensgraph.md`, contradiction semantics and human review requirements.

Product commit `5cf52f3bc8aaf5d3b4f628ec0fe15685e9b8ed34` adds `enqueue_canonical_contradiction_review()` in `src/athena/knowledge/contradiction_review_enqueue.py`.

The new composition boundary:

1. assesses the exact `left_revision_id` and `right_revision_id` with `assess_canonical_contradiction_candidate()`;
2. returns without persistence when deterministic temporal or attribution policy rejects candidacy;
3. otherwise delegates unchanged processing/model identity, entity/revision identity, confidence, reason and timestamp to the existing `ReviewService.enqueue_contradiction()` persistent boundary.

No review row is created for a deterministic rejection. Missing exact revisions retain the existing fail-closed exception path. Existing review deduplication, durable schema, stale-revision acceptance checks, user decision semantics and contradiction-pair persistence are unchanged.

Focused acceptance commit `53b699cf3554836001672422937ea89fc666d7b6` locks no-enqueue on rejection and exact metadata/revision delegation on permission.

## Verification

- Combined predecessor exact Quality `33925078295`: `success`.
- Current product/test head `53b699cf3554836001672422937ea89fc666d7b6`: canonical Quality `33928921951` is pending; no PASS is claimed yet.
- No Skip/XFail, weakened assertion, fake provenance, fake PALLAS state or alternate persistence implementation was introduced.

## Ownership / collision avoidance

- Backend deep storage/runtime/recovery work remains untouched.
- UI presentation/Qt work remains untouched.
- Error worker owns independent error-ledger verification; no new stable Core error signature is claimed.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Integrator handoff

READY now: combined exact-revision contradiction gate lineage `b10bdc52eba9449a105a0db57466771ad4412a63` + `8eab1e513a5957a01e1c3e2afcdeaa885965de96` + `b1da19a0aab5a80bc9cef06ff68cf92dfdb61317`, exact green Quality `33925078295`.

NOT READY yet: contradiction-review persistence composition `5cf52f3bc8aaf5d3b4f628ec0fe15685e9b8ed34` + `53b699cf3554836001672422937ea89fc666d7b6` until canonical Quality `33928921951` (or an exact superseding product-containing run) is green.

## Next Alpha/Beta gap

Consume canonical Quality for the new enqueue composition. If green, hand it READY to Integrator and trace the real model/extraction call site that currently invokes `ReviewService.enqueue_contradiction()` directly; replace only that call site with `enqueue_canonical_contradiction_review()` so the deterministic gate is on the actual production path. Preserve exact revision identity, existing transaction ownership, review deduplication, human-control semantics and all provenance/persistence invariants.
