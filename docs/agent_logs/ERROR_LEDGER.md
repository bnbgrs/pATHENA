# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@3231615650473fd549a7d852fb3bbe215f7b721f`; canonical Quality `34811112376 = IN_PROGRESS`. Do not mutate Develop or start a competing canonical run.
- `postmerge/errors@60e53eca416724c6cb8c3bc43c78ef057561ac53`; exact canonical `34808200586 = FAILURE`. This branch still carries inherited stale 48px UI geometry; no current Error-owned release/storage failure is established.
- `postmerge/spec-core@ae82147ab8de6d3805bb5f2299497296af8ff19f`; exact canonical `34809576476 = SUCCESS`. No current matching Core failure is open.
- `postmerge/backend@52eb61de9ecfde4074778a1bab2966e18aab526d`; latest known exact canonical remains green. Keep closed absent a new exact matching failure.
- `postmerge/ui@e8b8eb716efea4d8780d0487e26f5d7b9ebab230`; exact 11-Surface Visual `34811244977`, attempt 2, `FAILURE`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0063 — P2 — current UI visual capture route identity drifts before Files capture

Status: `OPEN`

Owner: UI / visual harness-product boundary. Error worker is evidence-only; do not patch UI product code in parallel.

Exact reproduction: `postmerge/ui@e8b8eb716efea4d8780d0487e26f5d7b9ebab230`, Visual `34811244977` attempt 2. Harness Ruff, comparator mypy/tests, hierarchy-token and navigation-accessibility contracts all pass. Step `Capture exactly eleven canonical surfaces with native fonts` fails. The uploaded exact artifact contains only eight PNGs and `capture-wrapper-error.txt` with:

`workspace row 4: RuntimeError: Workspace route identity drifted before capture: requested row 4, navigation row 1, page index 1.`

The capture loop sets each of seven primary rows and fail-closes if `navigation.currentRow()` or `pages.currentIndex()` differs. Rows 0-3 capture successfully; row 4 reverts to Knowledge (row/page 1). Route-identity verification and baseline comparison are therefore skipped.

Required closure: UI reproduces and fixes the row-4 route transition without weakening the seven-page route identity contract, then obtains an exact-SHA capture with all eleven real surfaces. No comparator, route, baseline or verdict relaxation.

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `BLOCKED`

Owner: UI / Visual Review.

The current UI candidate cannot reach truthful 11-pair review because `ERR-0063` aborts native capture before Files/System/Settings are produced. Do not create or accept a baseline. After `ERR-0063` closes, UI must open all eleven exact reference/render pairs, record truthful pair states, and obtain exact-SHA final visual-verdict success.

## CURRENT REPRODUCTION / OWNERSHIP HANDOFF

### ERR-0059 — P2 — manifest capture truth reappears on stale UI harness lineage

Status: `BLOCKED`

The exact UI artifact for `e8b8eb716efea4d8780d0487e26f5d7b9ebab230` contains only eight `captures`, but its manifest falsely reports `captured_reference_count = 11` and all eleven surface names. This exactly reproduces the historical manifest-truth defect on the current UI worker SHA.

However, authoritative Develop and `postmerge/errors` already contain the bounded fix: `captured_reference_surfaces = [capture["label"] for capture in captures]`, `captured_reference_count = len(captures)`, `assigned_reference_count = 11`, with PASS still requiring exactly eleven captures. The UI branch is heavily diverged from current Develop and still carries the old constant manifest implementation. Therefore no duplicate Error-branch patch is permitted. UI must synchronize/port the already-fixed harness truth before its next visual candidate.

Do not mark this `FIXED` for the current UI exact SHA until an exact UI artifact demonstrates truthful partial capture metadata; do not weaken the fail-closed eleven-capture contract.

## FIXED / HELD CLOSED

- `ERR-0062` — `FIXED`; current Spec/Core canonical is green.
- `ERR-0060` — `FIXED`; current Spec/Core canonical is green.
- `ERR-0061` — `FIXED`; Core Focused enforces mypy.
- Historical `ERR-0058`, `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049` remain closed absent new exact reproduction.

## STALE / DEDUPLICATED CASCADES

### Error-worker inherited 48px UI geometry divergence

Status: `STALE`

The Error-worker lineage still carries the inherited Send-button 48px geometry against the authoritative 44px guard. Do not reopen the UI product defect, weaken the 44px guard, or patch UI in parallel from `postmerge/errors`.

## Persistent release guards

No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Keep guards unchanged.

## Next root cause

1. Consume terminal canonical result for `develop/pathena-next@3231615650473fd549a7d852fb3bbe215f7b721f`; open only a newly reproduced exact failure.
2. UI owns `ERR-0063`: fix the row-4 route drift and rerun the exact 11-surface capture.
3. On that UI successor, verify manifest truth; current UI reproduction of `ERR-0059` remains `BLOCKED` until the already-fixed harness logic is present and exact evidence is truthful.
4. `ERR-0054` remains `BLOCKED` behind technical capture completion; no baseline acceptance in parallel.
5. Keep Spec/Core and Backend closed while exact canonical-green.
