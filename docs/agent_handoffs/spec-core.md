# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@a7c1d8cd1530a3003690292a9bf4c660472d59ce`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization merged current Develop into the worker through PR #65 as `fcdb0976a47b6da839244785a3403de1df5444f9`. No `main` mutation occurred.

## Verified foundation

Develop verifies normal-Hybrid Search facade/application composition, temporal contradiction composition, canonical Exhaustive Research coverage accounting, canonical coverage result payload, and durable ResearchScope/ResearchResult coverage composition.

The prior formula-identity correction is also now canonically verified: exact Core handoff head `1863e4e761edc71d6f08a05b6cab211fcdc41fd8` passed ATHENA Quality Gate `33862929677` with conclusion `success`. Product `b1e93c5bd3121bcb8c871964e8a24b65a200694a` and focused test `9b4fe08205f50cbc57004044685058c5f01a51b5` therefore have exact product-containing green evidence.

That correction keeps the persisted Research job and canonical coverage payload on one stable formula identity: `eligible-success-or-irrelevant-v1`. Coverage arithmetic is unchanged.

## Implemented product slice — source-internal Research coverage

Beta Exhaustive Research §37 requires multi-part Sources to retain source-internal coverage rather than exposing only job-wide coverage. Repository/code search found no existing Core source-coverage policy on current Develop.

Product commit: `18715d6976dd05b7f511e5ecbc201130525fcf11`.
Focused test commit: `c9ea636de878dc5cfb4afae17aa5a6c452745c0e`.

`SourceCoverage` now provides one deterministic, source-identified coverage contract for required Research work units:

- stable formula identity `eligible-units-success-or-irrelevant-v1`;
- eligible units = unit_total - excluded_count;
- processed units = successful + irrelevant + failed + unavailable;
- coverage-positive units = successful + irrelevant only;
- failed/unavailable remain terminal and visible but never inflate coverage;
- zero eligible units cannot synthesize 100% coverage;
- impossible and bool/non-integer/negative counters fail closed;
- payload includes the real source UUID and all canonical counters.

No persistence schema, transaction, snapshot, recovery, fencing, idempotency, provider/transport, security, provenance, PALLAS or UI semantics changed. Persistence composition is deliberately a later bounded slice after the policy itself is green.

## Verification state

- Formula-identity exact handoff head `1863e4e761edc71d6f08a05b6cab211fcdc41fd8`: canonical Quality `33862929677` = `success`.
- New source-coverage product/test head `c9ea636de878dc5cfb4afae17aa5a6c452745c0e`: canonical Quality `33867401901` = `pending` at handoff update time.
- No PASS is claimed for SourceCoverage until an exact product-containing run completes successfully.
- No Skip/XFail, weakened assertion, fake source, synthetic provenance or decorative PALLAS state was introduced.

## Coordination

- Backend-owned Research runtime/input boundaries and deeper Storage/Recovery/System contracts remain untouched.
- UI-owned presentation/accessibility/visual files remain untouched.
- Error handoff currently records no open confirmed Core defect.
- `main` and `bnbgrs/ATHENA` remain read-only and unchanged.

## Integrator handoff

READY: formula-identity correction `b1e93c5bd3121bcb8c871964e8a24b65a200694a` + `9b4fe08205f50cbc57004044685058c5f01a51b5`, backed by exact green Core handoff head `1863e4e761edc71d6f08a05b6cab211fcdc41fd8` / Quality `33862929677`.

NOT READY: source-internal Research coverage `18715d6976dd05b7f511e5ecbc201130525fcf11` + `c9ea636de878dc5cfb4afae17aa5a6c452745c0e` until exact canonical Quality `33867401901` is green.

## Next Core action

Consume exact Quality `33867401901`. If green, hand SourceCoverage to Integrator as READY and take the next bounded Beta §37 composition gap: persist source-internal coverage only from real per-source Work Units/Candidates, retaining source identity and failed/unavailable visibility without duplicate arithmetic or fabricated coverage. If the source-coverage policy itself fails canonical checks, fix only the exact Core-owned root cause first.
