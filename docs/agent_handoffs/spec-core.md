# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@14adeb8949f680dc16a3067e586b3950132e0375`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization with current Develop: merge commit `94a6ff111d62a98fa7a010c84f2c4f467f0713af` (parents previous Core head `fe356aa1fdea519d1391e61a3694c4e19d92fabc` and exact Develop SHA). No `main` mutation occurred.

## Verified foundation

Develop verifies normal-Hybrid Search facade/application composition, temporal contradiction composition, canonical Exhaustive Research coverage accounting, canonical coverage result payload, durable ResearchScope/ResearchResult coverage composition, and source-internal Research coverage policy.

Real-record source coverage composition is now canonically verified: exact Core head `fe356aa1fdea519d1391e61a3694c4e19d92fabc` passed ATHENA Quality Gate `33877310215` with conclusion `success`. This verifies the bounded product/test lineage `d8f0c42a94ded684e3e9a9980c3a875da37b5f06` + `585908f1459bbf251b3c463706e6b09db7f9e1d8` plus typing-only correction `fe356aa1fdea519d1391e61a3694c4e19d92fabc`.

## Implemented product slice — storage-ready source coverage payload composition

Beta Exhaustive Research §37 requires source-internal coverage to be stored for multipart Sources. The next bounded Core step now converts the verified real Candidate/Work record composition directly into deterministic Core-owned ResearchResult-ready payloads.

Product commit: `4c5b1364bce18f572c949f3134df7d9b61947242`.
Focused test commit: `27e3f3e444e9caf164f6a34c82b4dc041950be38`.

`source_coverage_result_payloads_from_records()`:

- accepts only real `ResearchCandidateRecord` / `ResearchWorkItemRecord` inputs;
- delegates all arithmetic and validation to the already verified `source_coverages_from_records()` + `SourceCoverage.result_payload()` contracts;
- preserves stable per-source UUID ordering;
- emits the stable source-coverage `formula_id` and exact terminal counters;
- keeps failed/unavailable units visible and non-coverage-positive;
- does not synthesize source identity, provenance, PALLAS state, or completion;
- introduces no schema, transaction, snapshot, recovery, fencing, idempotency, provider/transport, security, or UI change.

Repository finalization does not yet embed these payloads into `ResearchResult.content_json`; that is the next bounded mutation. This run intentionally avoids a second arithmetic implementation before the storage-ready payload contract is independently verified.

## Verification state

- Real-record source coverage composition exact head `fe356aa1fdea519d1391e61a3694c4e19d92fabc`: canonical Quality `33877310215` = `success`.
- Storage-ready source coverage payload product/test head `27e3f3e444e9caf164f6a34c82b4dc041950be38`: no exact workflow run is currently attached/observed; no PASS is claimed.
- Local checkout execution remains unavailable because `github.com` DNS resolution fails in the execution environment; GitHub connector mutation remained available and was used safely.
- No Skip/XFail, weakened assertion, fake source, synthetic provenance or decorative PALLAS state was introduced.

## Coordination

- Backend-owned Research runtime/input boundaries and deeper Storage/Recovery/System contracts remain untouched.
- UI-owned presentation/accessibility/visual files remain untouched.
- Error handoff records no open confirmed Core blocker relevant to this slice.
- `main` and `bnbgrs/ATHENA` remain read-only and unchanged.

## Integrator handoff

READY: real-record source coverage composition `d8f0c42a94ded684e3e9a9980c3a875da37b5f06` + `585908f1459bbf251b3c463706e6b09db7f9e1d8` + typing-only fix `fe356aa1fdea519d1391e61a3694c4e19d92fabc`, backed by exact green Core head `fe356aa1fdea519d1391e61a3694c4e19d92fabc` / Quality `33877310215`.

NOT READY: storage-ready source coverage payload composition `4c5b1364bce18f572c949f3134df7d9b61947242` + `27e3f3e444e9caf164f6a34c82b4dc041950be38` until exact canonical Quality is green.

## Next Core action

Obtain/consume exact canonical Quality for the current payload head. If green, hand the bounded payload commits READY and wire `source_coverage_result_payloads_from_records()` into `ResearchRepository.finalize_result_fenced()` so `ResearchResult.content_json` durably stores source-internal coverage from the same real Candidate/Work rows, with the new field reserved from semantic/model content and without duplicate arithmetic, schema broadening, fabricated coverage, or changes to snapshot/recovery/idempotency/provenance semantics.
