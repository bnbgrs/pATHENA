# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Integration baseline: `develop/pathena-next@5bfa74e47ee9874b9df2055a0d50d46bc82d3cbb`.
- Exact canonical Quality on that baseline: `34808031326 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- Worker branch: `postmerge/spec-core`.
- Previous worker `2c1aef57d1ffd5ab53283a05843c912c9e3e93ad` is already integrated/closed and is not a current product target.

## Source-of-truth result

Current Develop already contains the transport-neutral `KnowledgeInspectionApiService` added by `5bfa74e47...`. It adapts the existing repository-backed `KnowledgeInspectionService` into canonical Claim, provenance/evidence, and contradiction-review DTOs. The adapter itself is already integrated and must not be duplicated.

`CoreApiFacade` did not yet expose an attachment boundary for that adapter, so desktop/future transports could not discover or call canonical Claim inspection through the central API facade. This is the selected independent Core composition gap for this worker slice.

## Selected product slice — Claim inspection through CoreApiFacade

The worker candidate adds a bounded facade attachment without changing Storage, repository behavior, Claim semantics, contradiction-review semantics, Security, Recovery, packaging, or UI.

`src/athena/api/service.py` now:

- accepts `KnowledgeInspectionApiService` through a strict single-attach boundary;
- advertises `knowledge.claim.inspect` and `knowledge.review.contradiction` only while the real adapter is attached;
- exposes canonical Claim list/load/history calls by exact delegation;
- exposes pending/load/resolve contradiction-review calls by exact delegation;
- fails closed when inspection is unavailable;
- performs no DTO rewriting, identity fabrication, actor fabrication, repository access, or alternate persistence.

`tests/unit/test_api_knowledge_inspection_facade.py` focuses the new composition boundary:

- capability absent before attachment and present after attachment;
- duplicate attachment rejected;
- calls fail closed before attachment;
- Claim/review identifiers, limits, and decisions are delegated unchanged;
- returned adapter objects are not rewritten by the facade.

The already-integrated adapter remains responsible for UUID parsing, canonical DTO conversion, typed `confirm`/`reject` decisions, and actor acquisition through its injected provider.

## Ownership / collision avoidance

- Application auto-wiring remains a distinct next Core slice; this candidate does not invent a second application facade or actor path.
- The canonical local actor source remains `ChatService.ensure_local_user()`; application composition must inject that existing UUID provider into `KnowledgeInspectionApiService` rather than fabricate identity.
- Backend owns deep Storage/transaction/system work. No repository or schema path is duplicated here.
- UI owns styling/Qt presentation. No UI files are touched.
- No fake Claims, fake provenance, fake evidence, or synthetic review records are introduced.

## Qualification state at commit construction

- Baseline `5bfa74e47...`: canonical Quality `34808031326 = SUCCESS`.
- Candidate focused/canonical exact-SHA qualification: pending branch publication.
- No READY claim until focused tests and canonical Quality complete on the exact worker SHA.

## Next distinct Core gap

After this facade slice is exact-qualified and integrated, compose the already-existing domain/API inspection services in `AthenaApplication` using the real `ClaimRepository`, existing `ReviewService`, and `ChatService.ensure_local_user()` actor provider, then attach that exact `KnowledgeInspectionApiService` instance to `CoreApiFacade`. Focused acceptance should verify application instance identity and real repository-backed Claim/provenance/review reads without introducing a parallel persistence path.
