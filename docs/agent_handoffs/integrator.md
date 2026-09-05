# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `49212a0f157d433d68e9d04e9a9643e2909b6827`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `e0d009c4ecc2e0db3000acdb4b0dc726e64005de`; spec-core `4df931d3e9ea5d60952c92f9c8b93ef54e3d23e3`; backend `fea46376a3b3e642d394db4884501310cce155b8`; ui `074c7b9a4ccf9271a91dd1e56784601f749ac020`.
- `main` and `bnbgrs/ATHENA` were untouched.

## Integrated this run — Historical Backfill persisted Source boundaries

READY Core lineage independently reviewed:

- verified product/test head `2f62d2a26f9341e7ea8c84abe2ae48762bfe117c`;
- exact Historical Backfill focused test blob `c25b4ac25fd84fe0ce6a0174c1665120d17b8284`;
- canonical ATHENA Quality `33977608224 = success`;
- history-preserving synchronization head `015b0e39376d03bfaea21c6a1e26efa93f6819c3`, based on Develop `49212a0f157d433d68e9d04e9a9643e2909b6827`, differed from that Develop only in `tests/unit/test_research_historical_backfill.py` (+82 lines).

Current Develop already carried the truthful Historical Backfill production path and preceding bounded Research changes. The exact verified test blob was therefore overlaid directly onto current Develop rather than transplanting the older worker tree.

Integration commit: `83220947003b9e00dfe47c26e47b590f8a2df94c`.

## Contract now covered

- real `AthenaApplication` + `SourceCaptureService`/`SourceRepository` persistence path is exercised;
- lower and upper Historical Backfill time boundaries are inclusive;
- sources below/above the interval are excluded;
- sources committed after the pinned Research snapshot are excluded even when their acquisition timestamp lies inside the interval;
- truthful `ResearchMode.HISTORICAL_BACKFILL`, exact snapshot identity, persisted provenance and explicit local-only scope remain unchanged;
- no Project/Domain/Internet/Protected/Archive scope broadening, synthetic Sources/Claims/Evidence/PALLAS data, or Security/Storage/Transport/Recovery/UI behavior changes were introduced.

## Validation state

- Exact Core canonical Quality: `33977608224 = success` on `2f62d2a26f9341e7ea8c84abe2ae48762bfe117c`.
- Independent compatibility compare `49212a0f...015b0e39` showed exactly one modified file: `tests/unit/test_research_historical_backfill.py`, +82/0.
- Current Develop exact post-integration workflow lookup for `83220947003b9e00dfe47c26e47b590f8a2df94c` returned no associated workflow run yet; repository-wide global green is not claimed.

## Other current inputs

- Backend threshold-consistency is now READY: product `c0ee910a20fb396b0c20429f2da33873b407c641` + test `dde63f019c5ecd95d1805ff9c19fdd986fe4b436`, exact green descendant `5b04d7e335823f59bd33847e5b5c2c5b7e23458c`, Quality `33978168395 = success`.
- Backend assessment-state truth remains APPLIED / CANONICAL_PENDING.
- UI-GAP-0025 is READY: product `b3deae1671a8832e94fd8b3ef85fefa916ced468` + focused coverage `b25bc07059bc116ec25a4e7ce924a89f4508e2df`, exact synchronized head `fb98e47fde410137b971a303678d4e63f66e1d6d`, Quality `33978582156 = success`.
- UI-GAP-0026 remains IMPLEMENTED_PENDING_VERIFY.
- The exact-green UI successor `33978582156` did not reproduce prior Qt/Desktop SIGSEGV `ERR-0014`; Error worker has not yet consumed that clean successor, so closure is handed back rather than invented here.
- All eleven UI screens remain implemented pending visual review; original visual references remain pending and no pixel-level MATCH is claimed.

## Tracker handling

`docs/development/ALPHA_BETA_PROGRESS.md` was read for current state, but the connector response was truncated before a complete safe replacement could be guaranteed. It was intentionally not rewritten to avoid destructive truncation.

## Next integration order

1. Prefer any newer exact-green bounded Core successor if independently compatible.
2. Otherwise integrate exactly one READY alternative after current-Develop compatibility review; Backend threshold-consistency and UI-GAP-0025 are both current READY candidates.
3. Do not integrate Backend assessment-state truth or UI-GAP-0026 until exact canonical green evidence exists.
4. Error worker should consume the clean UI Quality `33978582156` and either close `ERR-0014` as nondeterministic runtime/harness evidence or retain it only if a fresh exact recurrence exists.
5. Obtain exact-current-Develop Quality before any repository-wide green claim.

## Rules retained

- No direct work on `main`; no main promotion.
- No force-push, history rewrite or auto-merge.
- No Skip/XFail, weaker assertions, Security/Storage/Windows/Recovery/validator relaxation, fake success or fabricated provenance.
