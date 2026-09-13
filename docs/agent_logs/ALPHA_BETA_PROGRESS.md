# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. No invented completion percentage.

## Current baseline

- Develop head before this repair: `7b4779b7be8c19b9ca0acaa57f826d0da8478592`.
- Exact canonical Quality `34758273159 = FAILURE` solely on Ruff `I001` in the newly replaced Core-Focused workflow-contract test file.
- On that same exact SHA, canonical pytest, Linux Storage, Local Install including pypdf metadata, and Windows release guards succeeded.
- Persistent release guards remain mandatory and unchanged.

## Current integration state

- The source-age staleness and explicit user-correction product guards remain integrated.
- The Core-Focused workflow already contains the new `tests/unit/test_user_correction*.py` trigger and selector.
- This repair restores four pre-existing workflow-contract tests that were accidentally dropped, preserves the new user-correction assertions, and corrects the Ruff import-order regression using bounded Error-worker evidence `ebcb67f065b7cd890c55897c3e9b9d74f0da10f8`.

## Cross-cutting quality coverage

The repaired contract test again enforces:

1. `--diff-filter=ACMR` and deleted-path exclusion;
2. narrow Core-owned pytest-family selection;
3. Knowledge API Ruff-source selection;
4. remediation reset/worktree cleanliness;
5. user-correction trigger and focused-test selection.

This strengthens/restores mandatory quality coverage. No test is skipped or xfailed and no guard is relaxed.

## Current worker truth before mutation

- Errors `8400089c41ebcd0dc2b2dc86124cbe59f623f098` owns the bounded harness repair.
- Spec/Core `69e4eeb74e459edcbf0ab83936152822e25dcf00` has newer Core work requiring fresh exact qualification before promotion.
- Backend `d0693efea6067eb32c3edb2ecac3a7ed4ab36974` is tree-synchronized with the pre-repair Develop baseline.
- UI `662f4a2d8da02e4497f141cac938193cf08e9361` contains a broad UI delta and is not promoted wholesale.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical wherever newer exact-SHA evidence exists; current worker heads and exact CI take precedence.
- Eleven-screen status remains fail-closed; no visual `MATCH` without opened original reference plus real exact-SHA render.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

The resulting exact Develop SHA requires canonical Quality before any additional Develop mutation.
