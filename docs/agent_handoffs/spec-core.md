# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@da34f14284cd61eb0e23b4dc2ac1d7757b2b2e5a`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization merge: `b211a27431c687694577dec8469a1a5b40b02997`, with parents previous Core `769ae5aa74f785ee2c48c2f93de7111043b4622e` and current Develop `da34f14284cd61eb0e23b4dc2ac1d7757b2b2e5a`.

## Verified prior slice — Exhaustive Research coverage accounting

Canonical coverage policy remains integrated and verified. The durable Scope/Result composition patch is still versioned at `docs/agent_handoffs/spec-core-research-coverage-composition.patch` against exact repository blob `dde58860ae0008b8d24cb0a868fb9420faeef405`.

This run obtained the complete exact repository blob through the GitHub blob API, so the prior read/truncation blocker is not repeated. However, the available authenticated write actions still replace an existing file only from complete literal content and expose no patch/delta mutation endpoint. Local git checkout again failed DNS resolution of `github.com`. The large central repository file therefore remains intentionally unmodified rather than reconstructed unsafely.

## Implemented disjoint Core slice — canonical ResearchResult coverage formula payload

Spec anchors: Beta 11 §§35–39 and §50. Section 36 requires the exact coverage formula to be stored in ResearchResult; Section 50 requires Coverage and failed/unavailable areas to remain explicit.

Product commit `bd0e8c1810b98ea8f34f4f820d8d9b71e8bbe604` adds `COVERAGE_FORMULA_ID = "eligible-successful-irrelevant-v1"` and `ResearchCoverage.result_payload()`. The payload is derived only from already validated canonical counters and includes formula identity, eligible/processed counts, successful/irrelevant/failed/unavailable/excluded counts, and coverage ratio. It does not fabricate provenance or convert failures/unavailable work into coverage.

Focused-test commit `60a68e6ff4089139f07cf8207e3f773fd25606a0` pins the exact canonical payload including visible failed/unavailable counts and formula identity. Canonical Quality run `33848536310` is pending on that exact product/test head; no PASS is claimed.

## Product contract

- formula identity is stable and explicit;
- eligible = candidate_total - excluded_count;
- processed = successful + irrelevant + failed + unavailable;
- coverage-positive = successful + irrelevant only;
- failed/unavailable remain visible and never inflate coverage;
- zero eligible work cannot synthesize 100%;
- no storage schema, transaction, snapshot, recovery, fence, provider, security, provenance, PALLAS or UI semantics changed.

## Ownership / collision avoidance

- Backend owns Research runtime/source-types/input-boundary and WAL/system work.
- UI owns styling/Desktop/UI slices.
- Error owns independent defect ledger/recovery validation.
- Core retains durable coverage composition and canonical Research result truthfulness.

## Integrator handoff

NOT READY for the new formula-payload slice until exact Quality `33848536310` completes green. If green, independently review bounded product/test commits `bd0e8c1810b98ea8f34f4f820d8d9b71e8bbe604` + `60a68e6ff4089139f07cf8207e3f773fd25606a0`.

The durable Scope/Result composition patch remains not implemented and must not be inferred from its patch file.

## Next Alpha/Beta gap

1. Consume exact Quality `33848536310`.
2. If green, integrate the formula-payload slice through Integrator review.
3. Continue the durable ResearchScope/ResearchResult composition using a safe authenticated mutation path; the complete exact blob is now available, but no large-file manual reconstruction is permitted.
4. Once composition is real and green, use `ResearchCoverage.result_payload()` at ResearchResult creation so the Beta-mandated exact formula identity is durably stored without duplicating coverage arithmetic.
