# Manual PALLAS edge-binding regression — 2026-09-14

## Exact base

- `develop/pathena-next@0ea74a990f8375039769c7726a327fd9142d5985`
- Post-#160 canonical Quality: `34839249527 = SUCCESS`
- #160 already integrated the living-field semantic-token cache. This slice does not reintroduce or modify that engine work.

## Scope

Regression evidence only. No production code changes.

`tests/unit/test_pathena_pallas_living_qt.py` now proves that after one deterministic living-field tick:

- the real bound `QGraphicsLineItem` starts at the living engine position of its source node;
- the same line ends at the living engine position of its target node;
- the real rendered source and target node items occupy those same engine coordinates.

This binds visible edge geometry to the already-implemented living node geometry instead of only checking semantic snapshot immutability and presentation properties.

## Ownership / collision boundary

- UI worker `postmerge/ui` was unchanged at `a88eac5f05db4128ae21b7c747e95c16a91191c4` during preparation.
- Backend worker owns WAL scheduler files only on its current net delta.
- Spec/Core owns Knowledge supersession files.
- Errors owns diagnostic/handoff evidence only.
- No PALLAS production file is changed here.

## Integration requirements

Require exact-head UI Focused Candidate and canonical Quality success on this branch, unchanged Develop base or an explicit fresh collision review, and final diff restricted to this test plus this handoff. Do not auto-merge.

After current-base integration, historical PR #161 can be closed as superseded: its token-cache product delta was consumed by #160 and its unique edge-binding regression is preserved here.