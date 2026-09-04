# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@b69a91a5781fd8d65b3643243c8feec60e4824f7`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization: `bc0fe403b9365a1ca2359aa2111c0c359d5595b2`, parents `ceb3682728aceb0b09893da6530dc38bc99f943a` and current Develop.
- Synchronization carried only the verified Core-owned attribution product/test blobs; the newer Develop handoff tree was retained rather than overwritten.

## Verified predecessor — attribution-aware contradiction policy

Spec anchor: `docs/beta/05_Wissenseinheiten_Claims_und_Wissensgraph.md` §59.

- Product: `2e88324d91b72656e6af707110989edffd25ec6a`.
- Acceptance correction: `ceb3682728aceb0b09893da6530dc38bc99f943a`.
- Exact canonical Quality: `33915587266 = success` on `ceb3682728aceb0b09893da6530dc38bc99f943a`.
- READY for Integrator review.

Contract: two explicit `ATTRIBUTED_OPINION` claims from distinct real `attributed_to_entity_id` values are not automatically promoted to an objective contradiction candidate. Same-attribution opinions and factual/mixed claims remain review-eligible. `ClaimDraft` continues to reject an attributed opinion without attribution; no identity is synthesized.

## Current product slice — exact-revision combined contradiction candidate gate

Product commit: `b10bdc52eba9449a105a0db57466771ad4412a63`.
Focused-test commit: `8eab1e513a5957a01e1c3e2afcdeaa885965de96`.
Status: `IMPLEMENTED_PENDING_VERIFY`.

`CanonicalContradictionCandidateAssessment` composes the existing deterministic temporal assessment with the verified attribution assessment. `permits_contradiction_candidate` is true only when both gates permit the pair.

`assess_canonical_contradiction_candidate()` loads the left and right Claim drafts by the exact requested revision IDs through the existing fail-closed `_load_claim_draft()` boundary, then applies both policies to those same loaded revisions. The existing `assess_canonical_claim_revisions()` temporal API is retained unchanged for current callers.

Focused acceptance covers:

- the same exact revision pair is used for both deterministic policies;
- overlapping factual claims remain candidate-eligible;
- provably temporally disjoint claims are rejected;
- distinct attributed opinions are rejected even when temporally eligible.

No persistence write, queue mutation, provenance synthesis, PALLAS simulation, schema, recovery, transport, security or UI behavior is changed.

## Coordination

- `errors.md`: no active stable Core root cause.
- `backend.md`: deep storage/runtime/recovery work remains Backend-owned and untouched.
- `ui.md`: presentation/Qt ownership remains UI-owned and untouched.
- `integrator.md`: normal Hybrid Search is already verified/integrated; no duplicate Search mutation was made.

## Integrator handoff

READY predecessor: attribution policy `2e88324d91b72656e6af707110989edffd25ec6a` + acceptance correction `ceb3682728aceb0b09893da6530dc38bc99f943a`, exact Quality `33915587266 = success`.

Combined exact-revision gate is NOT READY until canonical Quality succeeds on the product/test-containing worker head.

## Next Alpha/Beta gap

After exact green verification, hand the combined gate READY to Integrator. Then trace and implement the smallest real enqueue/composition boundary that consumes `permits_contradiction_candidate` before durable contradiction-review creation, preserving exact revision identity and fail-closed lookup. Do not create contradictions from different-speaker opinions or provably disjoint validity windows, and do not broaden persistence/schema semantics.
