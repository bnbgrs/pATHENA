# pATHENA Error Handoff

## Baseline

- Develop: `915668a376390d86fb333291f555eb804dfa4358` (`feat(backend): integrate schedule codec and startup identity hardening`).
- Develop canonical Quality `34718446158@915668a376390d86fb333291f555eb804dfa4358 = IN_PROGRESS`; no competing run started by Errors.
- Previous Develop `54c990285503e5076d31f46408ef530b9f02de28` canonical `34715466882 = SUCCESS`.
- Errors worker entered this run at `cbcb9f60981484554d39f614308b32b67f378787`; before mutation that exact SHA had zero workflow runs.
- Current workers: Spec/Core `47053f798bae152f676e9ff4be22ca4c6c06a6a8`; Backend `c40be5764e600fe961bc3aeaf39c17f91100e34f`; UI `8b38c1a501789cbfb7c76b1ee1acef999270fa13`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current error state

- OPEN: `ERR-0046`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0042`, `ERR-0043`, `ERR-0045`.
- FIXED: `ERR-0044`, `ERR-0041`, `ERR-0040`, `ERR-0035`, `ERR-0033` and prior closed clusters.
- STALE: `ERR-0038`, `ERR-0039` and prior stale clusters.

## ITERATION-1 — ERR-0042 owner repair verified

`ERR-0042 = FIXED_PENDING_VERIFY / P1`.

Spec/Core advanced from the historical red revision-change candidate to exact `47053f798bae152f676e9ff4be22ca4c6c06a6a8` (`fix(core): normalize revision explanation test import block`). Exact owner verification is now complete:

- Core Focused `34716645679 = SUCCESS`.
- canonical Quality `34716645678 = SUCCESS`.

The historical one-line Ruff `I001` is therefore repaired owner-side. Do not keep it OPEN from older runs. It is not `FIXED` yet because current Develop does not contain proven integration of this Spec/Core repair. Integrate the exact verified repair, then require canonical success on the resulting Develop SHA.

## ITERATION-2 — ERR-0043 integrated, waiting only Develop canonical

`ERR-0043 = FIXED_PENDING_VERIFY / P1`.

Backend synchronized to exact `c40be5764e600fe961bc3aeaf39c17f91100e34f`; exact qualification is fully green:

- Backend Focused `34717283972 = SUCCESS`.
- Storage Focused `34717283988 = SUCCESS`.
- canonical Quality `34717283963 = SUCCESS`.

Integrator handoff for Develop `915668a376390d86fb333291f555eb804dfa4358` explicitly states that `src/athena/storage/database.py` now accepts only a complete concurrent WAL+SHM publication for the same primary identity, re-inspects before acceptance, and keeps partial/foreign changes fail-closed. The bounded tests were integrated with it. No Storage/Recovery guard is relaxed.

Only final integrated canonical verification remains: `34718446158@915668a...` is still running. Mark `FIXED` only if it completes SUCCESS.

## ITERATION-3 — ERR-0045 integrated, waiting only Develop canonical

`ERR-0045 = FIXED_PENDING_VERIFY / P2`.

The valid sidecar-free test fixture is carried through the same fully green Backend exact `c40be5764e600fe961bc3aeaf39c17f91100e34f` and included in the bounded Develop integration `915668a...`. Backend Focused, Storage Focused and canonical are all green on the owner head.

Only `34718446158@915668a...` remains before final closure. No test, Storage, Recovery or startup guard was weakened.

## ITERATION-4 — ERR-0046 re-reproduced on newest UI exact SHA

`ERR-0046 = OPEN / P2`.

The previous UI reproducer is superseded by newer exact `postmerge/ui@8b38c1a501789cbfb7c76b1ee1acef999270fa13`:

- UI Focused `34717682781 = SUCCESS`.
- canonical Quality `34717682751 = SUCCESS`.
- Core Focused `34717682759 = FAILURE`.

Downloaded exact Core diagnostics show:

- Ruff: `All checks passed!`.
- focused pytest selects only `tests/unit/test_pathena_comfyui_shell.py` and `tests/unit/test_pathena_pallas_full_view.py`.
- both modules are skipped at collection because `PySide6` is absent.
- result: `2 skipped`, then the final outcome gate correctly refuses SUCCESS.

This is stronger deduplication evidence than the prior run: the same exact UI SHA is fully green in both UI Focused and canonical Quality, so no UI product regression should be opened.

Current Develop `core-focused-candidate.yml` still selects every changed `tests/unit/test_*.py` for focused pytest while the workflow trigger itself is Core-scoped and the lane installs only `--extra dev`. The root cause is therefore still current harness ownership selection.

Safe repair remains narrow: make focused pytest selection mirror explicit Core-owned patterns (claim, knowledge, concept-note, identity-transition, temporal) or another explicit Core allowlist. Preserve deleted-file filtering, tracked-worktree fail-closed Ruff remediation, and final outcome enforcement. Never treat skipped-only execution as success.

Closure requires both: (1) an exact UI-only change where these UI tests are no longer selected by Core Focused, and (2) a negative-control Core test failure that still makes the lane fail, followed by integrated canonical success.

## ITERATION-5 — current Develop gate discipline

Current Develop `915668a...` canonical `34718446158` remains `IN_PROGRESS`. No duplicate canonical run was started. The run is the closure gate for integrated `ERR-0043` and `ERR-0045`; it must be consumed before another Develop-side closure claim.

## Integrator handoff

- `ERR-0042 = FIXED_PENDING_VERIFY / P1`: Spec/Core `47053f798...` exact Core Focused + canonical SUCCESS; integrate this exact verified one-line repair lineage and require resulting Develop canonical SUCCESS.
- `ERR-0043 = FIXED_PENDING_VERIFY / P1`: Backend product guard is integrated into Develop `915668a...`; close only if canonical `34718446158` succeeds.
- `ERR-0045 = FIXED_PENDING_VERIFY / P2`: test-fixture repair is integrated into the same Develop SHA; close only if canonical `34718446158` succeeds.
- `ERR-0046 = OPEN / P2`: newest UI exact `8b38c1a...` has UI Focused + canonical SUCCESS but Core Focused FAILURE with only two PySide6-dependent UI tests skipped. Repair Core ownership selection, never skip-to-green.

## CI discipline

- `postmerge/errors@cbcb9f60981484554d39f614308b32b67f378787` had zero workflow runs before the ledger mutation.
- Ledger commit `f677fa0039ac19a847af903b6fa12d733b26f881` also had zero workflow runs before this handoff mutation.
- No canonical run was started or duplicated by Errors.
- No product code or foreign worker branch was mutated.

## NEXT_ROOT_CAUSE

1. Consume `34718446158@develop/915668a...`; if SUCCESS, close `ERR-0043` and `ERR-0045` immediately with exact evidence; if FAILURE, classify only the exact failing signature.
2. Follow integration of Spec/Core `47053f798...`; `ERR-0042` closes only after integrated Develop canonical success.
3. Follow a harness successor for `ERR-0046`; require both the UI-only non-selection proof and a genuine Core-failure negative control.
4. After those transitions, scan current exact worker/canonical results for the next independent highest-impact cluster rather than reopening stale historical IDs.
