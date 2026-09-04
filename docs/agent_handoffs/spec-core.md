# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@606e9dc72278ec331856e998a1b3fb4fa4754787`.
- Stable read-only branch: `main` remains untouched.
- Worker branch: `postmerge/spec-core`.
- Previous worker head: `bdda15ce7f5a8b3b3ae426b85c7d2f0cc7759f79`.
- History-preserving NON-FORCE synchronization merge: `2c4de589429516ce5e3c242ecb030039d8c571d8`, parents `bdda15ce7f5a8b3b3ae426b85c7d2f0cc7759f79` and `606e9dc72278ec331856e998a1b3fb4fa4754787`.

## Verified prior Core state

Normal-Hybrid Search facade/application composition is already integrated on Develop and is not re-opened by this worker. ProposalAcceptanceService temporal contradiction composition is likewise already verified/integrated on Develop.

## Current bounded slice — Exhaustive Research coverage accounting

Spec anchor: `docs/beta/11_Exhaustive_Research.md` coverage/completeness requirements.

Product/test commits retained from the previous worker lineage:

- product `85daef5e4301a01c3b504d431e7998b7f2a9dc5b`;
- focused tests `336f0194a1c1e3c26a54571b367824e9044e1a31`.

Files:

- `src/athena/research/coverage.py`;
- `tests/unit/test_research_coverage.py`.

Contract:

- eligible work = candidate total minus explicit exclusions;
- processed work includes successful, irrelevant, failed and unavailable terminal work;
- coverage-positive work includes only successful and explicitly irrelevant work;
- failed/unavailable work never inflates coverage;
- zero eligible work never synthesizes a 100% coverage claim;
- bool, negative and impossible counters fail closed;
- no storage, transport, provider, UI, security, recovery, provenance or PALLAS mutation.

## Verification state

Previous canonical Quality run `33832553543` on old product/test head `336f0194a1c1e3c26a54571b367824e9044e1a31` failed. Ruff and specification validator passed, but mypy/pytest plus API runtime-path-boundary/local-install jobs failed on that stale pre-Develop lineage.

To distinguish stale-baseline regressions from this bounded Research policy, the worker was synchronized history-preservingly onto exact current Develop and canonical Quality was retriggered on merge head `2c4de589429516ce5e3c242ecb030039d8c571d8` as run `33836143224`.

Early evidence from `33836143224`: focused Linux storage regressions pass, but the shared API runtime path-boundary step and local-install Core/API restart smoke still fail before canonical Quality has completed. Those failures therefore persist even after current-Develop synchronization and are not silently attributed to Research coverage accounting. Final mypy/pytest state is still pending at handoff update time; no PASS/READY claim is made.

## Collision avoidance

Backend current worker head is independently advancing Research/runtime boundary validation. Core does not mutate Backend transport/storage/runtime-boundary code. UI and Error owned product files are untouched. Main is untouched.

## Integrator handoff

NOT READY. Do not integrate the Research coverage policy until canonical Quality or focused evidence establishes that the bounded product/test delta itself is green. Run `33836143224` is the exact synchronized-head verification source.

## Next Core step

Consume final diagnostics from `33836143224`. If Research coverage tests/mypy are green and remaining failures are demonstrably pre-existing shared runtime-boundary failures, provide bounded READY evidence to Integrator without absorbing Backend ownership. If the new Research policy itself fails, fix only that exact Core-owned root cause. After verification, compose the coverage policy into the durable ResearchScope/ResearchResult counter-update path while preserving snapshot/recovery/idempotency semantics.
