# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `d14aca9504021bdacadb89dc478ca41545ab4316`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `0017b4d83481ba46e020d12492eb5c1d0a5fca7a`; spec-core `bab57ac560c3d0fd43f2beb7501b3d4160a09064`; backend `876fcd4dcffbcca50ac6cf137b5299343135c0e8`; ui `5a5ba2681412c32c181e63026ce1b92574675d64`.
- `main` and `bnbgrs/ATHENA` were untouched.

## Integrated this run — truthful Local+Web Research enqueue/durable scope

READY Core lineage independently reviewed:

- product/test commit `6c5431f35951b7916e1db97138306de41a5da622`;
- exact verified descendant `eaa43526398c2e5abb6efb2ec2ae58c53178e878`;
- focused verification `33986943543 = success` with pytest `10 passed`, Ruff PASS and mypy PASS;
- canonical ATHENA Quality `33987002816 = success`.

The three pre-existing Develop product blobs matched the worker product-parent blobs exactly before integration: `src/athena/research/service.py`, `src/athena/jobs/payload_validation.py`, and `src/athena/external/gateway.py`. The new acceptance file `tests/unit/test_research_local_plus_web.py` was added from the exact verified product commit. Tooling-only workflow/helper removals from the worker commit were intentionally not transplanted.

Integration commit: `3ff86b3031ba98e99cbb4dc3718204eb9b0ddf1b`.

## Contract now covered

- `ResearchService.enqueue_local_plus_web()` requires an explicit UUID authorization and at least one captured external Source;
- persists truthful `mode=local_plus_web` and canonical non-null `internet_scope` with exact authorization id and captured Source ids;
- durable `research.exhaustive` validation accepts Local+Web only with canonical authorization/captured-source provenance and requires captured ids to exactly match `explicit_source_ids`;
- all non-Web Research modes still require null Internet scope;
- `ExternalResearchService` captures authorized URLs before delegating to truthful Local+Web enqueue;
- no candidate-freeze union expansion, Protected/Archive expansion, synthetic Source/Claim/Evidence/PALLAS data, Skip/XFail, assertion weakening, or Security/Storage/Recovery guard relaxation was introduced.

## Validation state

- Core exact descendant Quality `33987002816 = success` verifies the exact product/test lineage.
- Focused Core verification `33986943543 = success`: pytest 10 passed, Ruff PASS, mypy PASS.
- Compatibility review proved all three modified existing product files were byte-identical between current Develop and the worker product parent before overlay.
- Exact-current-Develop repository-wide green is not claimed until an associated post-integration Quality run is available.

## Other current inputs

- Core Local+Web candidate-freeze union remains PATCH_EXISTS_BUT_UNAPPLIED at `docs/agent_handoffs/spec-core-local-plus-web-freeze.patch`; do not treat as READY until separately applied and green.
- Backend assessment-state truth and reserve-provision free-space boundary remain READY candidates from previously green Backend lineage; consume at most one in a later run after current-Develop compatibility review.
- UI later focus gaps remain subject to exact green evidence before integration.
- `ERR-0014` remains STALE after repeated exact clean successors; reopen only if the exact exit-139 signature recurs.

## Next integration order

1. Apply/review the versioned Core Local+Web candidate-freeze patch if the Core worker remains tooling-blocked next cycle and no concurrent ownership mutation exists; verify focused Research tests and canonical Quality before keeping it.
2. Otherwise integrate exactly one READY Backend or UI successor after independent compatibility review.
3. Obtain exact-current-Develop Quality before any repository-wide green claim.

## Rules retained

- No direct work on `main`; no main promotion.
- No force-push, history rewrite or auto-merge.
- No Skip/XFail, weaker assertions, Security/Storage/Windows/Recovery/validator relaxation, fake success or fabricated provenance.
