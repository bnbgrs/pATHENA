# Manual Core Claim-inspection composition recovery — 2026-09-14

## Exact lineage

- Integration target: `develop/pathena-next`.
- Broken exact base: `5024a7c2b60c80083d1650ae924c89cb3085019e` (`feat(core): compose claim inspection services`).
- Base canonical run: `34815625453`.
- At repair start: Linux Storage, Windows Path Safety and Local Install were green; Specification Validator was green; Ruff and mypy were red; the full pytest step was still running.
- Recovery branch: `manual/core-claim-inspection-composition-fix-20260914`.
- `main` is untouched.

## Root cause

The new Core composition helper accepted `ClaimRepository` and passed it directly to `KnowledgeInspectionService`.

That violates the inspection service's existing `ClaimReader` contract. `ClaimReader` requires:

- `load(...)`
- `list(...)`
- `history(...)`
- `evidence(...)`
- `provenance_inputs(...)`

`ClaimRepository` deliberately exposes lower-level repository names instead:

- `load_current(...)`
- `list_current(...)`
- `list_revisions(...)`
- `list_evidence(...)`
- `list_provenance_inputs(...)`

The existing canonical `ClaimService` already adapts those repository methods to the exact `ClaimReader` names. `AthenaApplication` already constructs and owns that service as `self.claims = ClaimService(self.claim_repository, self.chat)`.

Therefore the safe repair is not a new repository, duplicate adapter, cast, `type: ignore`, or protocol weakening. The composition helper now accepts the existing `ClaimReader` boundary, so the application's canonical `ClaimService` is passed through unchanged.

## Bounded repair

Owned paths are exactly:

- `src/athena/core/knowledge_inspection.py`
- `tests/unit/test_core_knowledge_inspection_composition.py`
- `docs/agent_handoffs/manual-core-claim-inspection-composition-fix-20260914.md`

Changes:

1. remove the concrete `ClaimRepository` dependency from the Core composer;
2. type `claims` as the already-defined `ClaimReader` protocol;
3. preserve the existing `ReviewService` and actor-provider instances unchanged;
4. update the focused composition test to build a real `ClaimService` over a tiny read-only repository probe;
5. execute `api.list_claims(limit=7)` through the composed path, proving the previous repository/service method-name mismatch cannot survive as an identity-only test;
6. keep import ordering canonical for Ruff.

## Why this is a runtime bug, not only typing

With the broken composition, `KnowledgeInspectionService.list_claims()` calls `self._claims.list(...)`. A raw `ClaimRepository` has no `list` method, so the first real inspection request would raise `AttributeError` even if typing were suppressed. The recovery test explicitly crosses this boundary.

## Collision boundary

At repair start, `postmerge/spec-core` remained on `ae82147ab8de6d3805bb5f2299497296af8ff19f` and did not yet contain the newly integrated `src/athena/core/knowledge_inspection.py`. This recovery is therefore isolated from the current Spec/Core worker tree. Recheck that head before integration.

PR #144 (maintenance consolidation) is intentionally separate and must not absorb this Core repair. It is based on the broken Develop head and therefore cannot be integrated until Develop is repaired and #144 is reconstructed/reverified on the repaired green base.

## Verification contract

Before integration require exact-head:

1. Specification Validator PASS;
2. Ruff PASS;
3. mypy PASS;
4. focused composition regression PASS;
5. isolated Desktop API controller PASS;
6. remaining full pytest suite PASS;
7. Linux Storage PASS;
8. Windows Path Safety PASS;
9. Local Install smoke PASS;
10. fresh Develop/Spec-Core collision check.

Do not replace this fix with `cast`, `type: ignore`, `Any`, a weakened `ClaimReader`, duplicate repository construction, or an identity-only test.
