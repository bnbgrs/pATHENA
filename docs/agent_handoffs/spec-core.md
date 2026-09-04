# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@3cfef2c2ee67799066ceefaf9ea84287817f256a`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE sync: `f0814b01cc7fe0463c53c6c488c800cf88d7056b`.
- `main` remains read-only and untouched.

## Verified prior state

`docs/development/ALPHA_BETA_PROGRESS.md` on Develop marks the normal-Hybrid facade/application composition and the ProposalAcceptanceService temporal contradiction gate as VERIFIED. The Core worker therefore did not repeat those completed slices.

## Current Core slice — Exhaustive Research coverage accounting

Spec anchor: `docs/beta/11_Exhaustive_Research.md` §§35-39.

Product commit: `85daef5e4301a01c3b504d431e7998b7f2a9dc5b`.
Focused-test commit: `336f0194a1c1e3c26a54571b367824e9044e1a31`.
Canonical Quality run: `33832553543` (pending at handoff update).

`src/athena/research/coverage.py` adds a deterministic, fail-closed coverage policy for a frozen candidate set:

- eligible candidates are `candidate_total - excluded_count`;
- successful and explicitly irrelevant work units are coverage-positive;
- failed and unavailable work units are terminal/processed but never inflate coverage;
- 100% is only reported when every eligible unit is successful or irrelevant;
- an empty eligible set does not manufacture a 100% marketing claim;
- bool/negative counters, excluded > candidate total, and terminal work exceeding eligible candidates fail closed.

No persistence schema, transport, provider, UI, storage, security, recovery, claim, provenance, or PALLAS mutation is introduced.

Focused tests cover mixed success/irrelevant/failure/unavailable accounting, explicit full coverage, zero-eligible behavior, bool rejection, and impossible terminal-count rejection.

## Integrator handoff

Status: `IMPLEMENTED_PENDING_VERIFY`.

Do not integrate until canonical Quality run `33832553543` completes green on exact product/test head `336f0194a1c1e3c26a54571b367824e9044e1a31` (or an exact descendant with documentation-only change and equivalent product/test blobs).

## Next Alpha/Beta gap

After green verification, compose this policy into the existing durable ResearchScope/ResearchResult counter update path so persisted `processed_count` and `coverage_ratio` are derived from the same validated counters, while preserving snapshot/recovery/idempotency semantics and exposing failed/unavailable work without hiding incompleteness.
