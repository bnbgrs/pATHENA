# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@66a8953629a7bce28e19479c9309a016c62ee63a`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization merge: `09061bcb45e813e784baee6183681b8bbae4b27a`, with parents previous Core `b647e17fb972c9acada8e5d77296be8ebd27c860` and current Develop `66a8953629a7bce28e19479c9309a016c62ee63a`.

## Verified prior slice — ResearchResult coverage formula payload

Canonical ATHENA Quality Gate run `33848576424` completed `success` on exact Core head `b647e17fb972c9acada8e5d77296be8ebd27c860`. The bounded formula-payload product/test lineage is therefore READY for independent Integrator review: product `bd0e8c1810b98ea8f34f4f820d8d9b71e8bbe604` plus focused tests `60a68e6ff4089139f07cf8207e3f773fd25606a0`.

The contract remains: formula identity `eligible-successful-irrelevant-v1`; eligible = candidate_total - excluded_count; processed = successful + irrelevant + failed + unavailable; coverage-positive = successful + irrelevant only; failed/unavailable remain explicit and do not inflate coverage; zero eligible work does not synthesize 100%.

## Current slice — durable ResearchScope/ResearchResult coverage composition

Source patch: `docs/agent_handoffs/spec-core-research-coverage-composition.patch`.

This run advanced the previously repeated tooling blocker in two concrete ways:

1. Core was NON-FORCE synchronized with current Develop through the Git Data tree/commit/ref mutation path, without local checkout and without overwriting foreign worker files.
2. The exact full `src/athena/research/repository.py` base blob `dde58860ae0008b8d24cb0a868fb9420faeef405` was read successfully through the dedicated GitHub blob endpoint. No truncated read is being used as mutation input.

The focused acceptance test from the versioned patch was applied as real repository file `tests/unit/test_research_coverage_persistence.py` in commit `da0d10a798c11a3047466776534b2bbdcd768b1a`. It pins that `_recompute_scope_counters()` delegates to canonical `ResearchCoverage`, with four eligible terminal units yielding processed=4 and coverage=0.5 while failed/unavailable remain non-coverage.

The product hunk in the large existing `repository.py` is not yet committed. The remaining connector limitation is now precise: available authenticated writes accept complete replacement content or Git object blobs/trees, but there is no delta/apply-patch action and connector results cannot be directly piped from the fetched full blob into `create_blob`. Local git remains DNS-blocked. The branch therefore intentionally does not reconstruct the large file from shortened output.

Canonical Quality run `33852735339` was created for the exact acceptance-test head `da0d10a798c11a3047466776534b2bbdcd768b1a`; it is pending at this handoff update. No PASS is claimed for the current composition slice.

## Ownership / collision avoidance

- Backend owns Research runtime/source-types/input-boundary and WAL/system work.
- UI owns styling/Desktop/UI slices.
- Error owns independent defect ledger/recovery validation.
- Core owns canonical Research coverage accounting, durable Scope/Result composition, and Research result truthfulness.
- Current Backend/UI/Error worker heads were inspected before mutation; this Core slice does not touch their owned product files.

## Integrator handoff

READY only for the already-green formula-payload lineage `bd0e8c1810b98ea8f34f4f820d8d9b71e8bbe604` + `60a68e6ff4089139f07cf8207e3f773fd25606a0`, backed by exact green Core head `b647e17fb972c9acada8e5d77296be8ebd27c860` / Quality `33848576424`.

NOT READY for durable repository composition. `tests/unit/test_research_coverage_persistence.py` is now real, but the corresponding product hunk must be committed and verified before integration.

## Next Alpha/Beta gap

1. Apply the existing product hunk to exact `repository.py@dde58860ae0008b8d24cb0a868fb9420faeef405` using a safe full-blob replacement path; do not repeat analysis-only handling of this blocker.
2. Verify `tests/unit/test_research_coverage.py`, `tests/unit/test_research_coverage_persistence.py`, the smallest Research repository/result regressions, then canonical Quality.
3. Once green, compose `ResearchCoverage.result_payload()` into ResearchResult creation so the exact formula identity and the same canonical problem counters are durably represented without duplicate arithmetic.
