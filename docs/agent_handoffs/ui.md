# pATHENA UI Handoff

## Current baseline

- Develop baseline reviewed: `develop/pathena-next@7617509e405c47fd872ad49f9a047e098c9f06a0`.
- Worker prior exact-green head: `a426469b503c6276cd6d1fd3ed6d89be0af67948`.
- Worker branch: `postmerge/ui`.
- `main` and `bnbgrs/ATHENA` remain read-only; no force push, history rewrite or main mutation occurred.

## Exact evidence consumed

ATHENA Quality Gate `34291934346` completed `success` on exact UI head `a426469b503c6276cd6d1fd3ed6d89be0af67948`. The bounded worker delta against its Develop merge base consists only of the shared design-token palette plus four UI contract tests. Current Develop advanced one disjoint commit, `7617509e405c47fd872ad49f9a047e098c9f06a0`, adding only an adaptive DirectChat reserve regression and Integrator handoff update; those changes do not collide with the UI palette product/test files.

## UI-GAP-0004 — reference-backed black/orange visual foundation

Status: `FIXED_ON_WORKER / INTEGRATOR_READY` pending verification of the synchronized documentation descendant.

The opened user references establish a consistent direction: near-black neutral canvas/panels, bright typography and sparse functional orange. The pre-fix design tokens were navy/blue-led and used `#377DFF` as the primary accent. The verified UI slice changes the shared visual foundation to deep neutral black surfaces and exact orange `#F26A21` while retaining semantic state colors, WCAG contrast, focus/accessibility and shell geometry contracts.

Product/test files:
- `src/athena/desktop/pathena_design_tokens.py`
- `tests/unit/test_pathena_design_tokens.py`
- `tests/unit/test_pathena_design_system.py`
- `tests/unit/test_pathena_theme.py`
- `tests/unit/test_pathena_window.py`

Exact verification: `a426469b503c6276cd6d1fd3ed6d89be0af67948` -> Quality `34291934346 = success`.

No screenshot-level `MATCH` or pixel parity is claimed because a rendered current build has not yet been opened beside every original reference.

## Reference evidence state

Actual user reference pixels have been directly opened for Workspace/Chat, Knowledge/PALLAS, Evidence/Inspector, Research and a multi-screen Chat/Knowledge/Research/Jobs composition. Per-slot manifest entries reflect only what was actually opened; remaining slots stay `VISUAL_REFERENCE_PENDING`.

## Collision / ownership

Current Develop's adaptive 2048-context DirectChat test remains Core/Integrator-owned and is preserved. UI changed no Backend, Storage, Security, Provider, scheduler/worker, process-spawn or recovery semantics. Historical runtime signatures remain Beta/release guards only unless reproduced on the current exact SHA.

## Integrator handoff

Integrator may independently review/import UI-GAP-0004 from the exact-green worker lineage `a426469b503c6276cd6d1fd3ed6d89be0af67948`. The product/test delta is bounded to the five visual-token contract files listed above and is compatible with current Develop `7617509e405c47fd872ad49f9a047e098c9f06a0` by disjoint-file comparison. Preserve the current Develop adaptive DirectChat boundary regression.

## Next UI gap

After the synchronized current-Develop descendant is canonical green, use the opened reference pixels plus an actual current render to pick at most one highest visible hierarchy/spacing/typography/composer/inspector mismatch. Do not rework UI-GAP-0001 through UI-GAP-0004 unless a current exact-SHA regression reproduces them.
