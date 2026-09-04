# pATHENA Backend & Systems Handoff

## Baseline

- Current integration base reviewed: `develop/pathena-next@5522e73c6f314b1dfac77fa5cfdb8e8d6f667704`.
- Worker branch: `postmerge/backend`.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.
- History-preserving NON-FORCE synchronization merge: `75ae07fdb0bf72c100cc8401f7881ffa03b96b03`, parents `577e8f9c7730836713816d70ca6b2fca43762a79` and current Develop `5522e73c6f314b1dfac77fa5cfdb8e8d6f667704`.
- The merge tree starts from current Develop and retains only Backend-owned Research boundary deltas plus this handoff; comparison against Develop is limited to `src/athena/research/service.py`, `tests/unit/test_research_stable_strings_boundaries.py`, and this handoff.

## Current backend slice — Research source-types container boundary

Product/test commit `5f9f3713c53c16375453c4a0f6be9a9a086700d6` introduces `_stable_source_types(values: object)`, rejects scalar text-like and non-Sequence containers, retains the existing per-element `SourceType` guard, and preserves deterministic `.value` sorting/deduplication. `ResearchService.enqueue_local()` routes `source_types` through this helper before actor setup, snapshot pinning or durable job creation.

The first Quality run on the product commit (`33837041846`) was `action_required` with zero jobs and is explicitly not PASS evidence.

After the non-force synchronization merge, canonical Quality run `33840621670` has four real jobs. Current evidence at this handoff update:

- Local install smoke: PASS.
- Linux storage regressions: PASS.
- Windows path safety: PASS.
- Python 3.12 quality: specification validator PASS, Ruff PASS, mypy PASS, full pytest still IN_PROGRESS.

Therefore the source-types slice remains `FIXED_PENDING_VERIFY`; no global PASS/READY claim is made until full pytest and the final canonical result complete successfully.

## Previously verified Research boundaries retained

- String-filter container product/test commit `818e421ea721003e16447ce8e335e49388dc1520`; focused verifier `33829758780` = SUCCESS.
- UUID-filter container product/test commit `462fba22637e0083c87df32f987134ce0fb3de00`; focused verifier `33833496929` = SUCCESS.
- Current synchronization preserves both exact boundary behaviors while incorporating current Develop history.

## Retained invariants

- Research persistence, snapshot pinning and durable job creation semantics remain unchanged for valid inputs.
- ExternalAccessGateway authorization/audit/provenance/TOR/redirect/fsync/transactional Source behavior is untouched.
- No retries, cryptography, storage, recovery, Windows/Linux path or packaging behavior changed.
- No skip/XFail, assertion weakening or guard weakening.

## Integrator handoff

NOT_READY pending completion of canonical Quality `33840621670` on synchronized exact product head `75ae07fdb0bf72c100cc8401f7881ffa03b96b03`. If and only if that run completes green, independently review the bounded source-types product/test delta originating at `5f9f3713c53c16375453c4a0f6be9a9a086700d6`; do not treat the earlier zero-job run as evidence.

## Next backend slice

First consume `33840621670`. If green, mark the source-types boundary READY and scan the next highest evidence-backed Research/Jobs/Storage/Recovery/Provider/Packaging gap. If red, classify and fix the exact primary failure before unrelated work.