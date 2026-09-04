# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@3ea908affd23f1d80e0b863a6af8cf366e2b8484`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization with current Develop: merge commit `e526173a6c0a60c316ae5f9ee1d3400dc1db18cf` (parents previous Core head and exact Develop SHA). No `main` mutation occurred.

## Verified foundation

Develop verifies normal-Hybrid Search facade/application composition, temporal contradiction composition, canonical Exhaustive Research coverage accounting, canonical coverage result payload, and durable ResearchScope/ResearchResult coverage composition.

Formula identity remains `eligible-success-or-irrelevant-v1` and is canonically verified.

Source-internal Research coverage policy is now also canonically verified: exact Core handoff head `0261a299b8703aec41c6032be0bb6e03d2aba637` passed ATHENA Quality Gate `33867459130` with conclusion `success`. Product `18715d6976dd05b7f511e5ecbc201130525fcf11` and focused test `c9ea636de878dc5cfb4afae17aa5a6c452745c0e` therefore have exact product-containing green evidence.

## Implemented product slice — real-record source coverage composition

Beta Exhaustive Research requires source-internal coverage for large/multipart Sources, and its Work Unit contract requires status to come from real persisted work rather than marketing or synthesized completeness.

Product commit: `d8f0c42a94ded684e3e9a9980c3a875da37b5f06`.
Focused test commit: `585908f1459bbf251b3c463706e6b09db7f9e1d8`.

`source_coverages_from_records()` composes the verified `SourceCoverage` policy directly from real `ResearchCandidateRecord` and `ResearchWorkItemRecord` identity/state:

- groups candidates by their real `source_id`;
- derives terminal counters only from matching real work-item states;
- pending eligible candidates remain uncovered rather than being invented as terminal;
- excluded duplicate candidates remain excluded and do not inflate coverage;
- failed/unavailable remain visible and never coverage-positive;
- unknown candidate references and multiple work records for one candidate fail closed;
- result order is stable by source UUID;
- no synthetic source/provenance/PALLAS data is introduced.

This slice deliberately does not add or alter persistence schema. Repository-level durable embedding remains the next bounded step after this composition is verified.

## Verification state

- SourceCoverage policy exact handoff head `0261a299b8703aec41c6032be0bb6e03d2aba637`: canonical Quality `33867459130` = `success`.
- Current real-record composition product/test head `585908f1459bbf251b3c463706e6b09db7f9e1d8`: canonical Quality `33871914294` = `pending` at handoff update time.
- No PASS is claimed for real-record composition until an exact product-containing run completes successfully.
- No Skip/XFail, weakened assertion, fake source, synthetic provenance or decorative PALLAS state was introduced.

## Coordination

- Backend-owned Research runtime/input boundaries and deeper Storage/Recovery/System contracts remain untouched.
- UI-owned presentation/accessibility/visual files remain untouched.
- Error handoff records no open confirmed Core blocker relevant to this slice.
- `main` and `bnbgrs/ATHENA` remain read-only and unchanged.

## Integrator handoff

READY: source-internal Research coverage policy `18715d6976dd05b7f511e5ecbc201130525fcf11` + `c9ea636de878dc5cfb4afae17aa5a6c452745c0e`, backed by exact green Core handoff head `0261a299b8703aec41c6032be0bb6e03d2aba637` / Quality `33867459130`.

NOT READY: real-record source coverage composition `d8f0c42a94ded684e3e9a9980c3a875da37b5f06` + `585908f1459bbf251b3c463706e6b09db7f9e1d8` until exact canonical Quality is green.

## Next Core action

Consume exact Quality for the current composition head. If green, hand the bounded composition commits READY and implement repository/result persistence of these source-identified payloads from the same real Candidate/Work records without duplicate arithmetic, schema broadening, fabricated coverage, or changes to snapshot/recovery/idempotency/provenance semantics. If Core-owned diagnostics fail, fix only the exact root cause first.
