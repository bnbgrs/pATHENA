# pATHENA UI Handoff

## Current baseline — 2026-09-11 18:41 CEST

- Run-start Develop: `develop/pathena-next@fec368f50307a9e24038baca3a80b10ee2a3c4fc`.
- Run-start worker: `postmerge/ui@f94a6d1edaddd2c4fc009f60134fd1bce6440500`.
- Exact Quality for `f94a6d1…`: run `34617691648 = SUCCESS`.
- Current bounded product correction: `b6aaaac887535bfcafa7e5784d0dc0b590758f36` (`ui: preserve primary pages when hosting help`).
- `main` and `bnbgrs/ATHENA` remain READ-ONLY and untouched.
- Current Spec/Core, Backend, Errors, Integrator, 11-screen manifest and Visual Gap Ledger were consumed before product work.

## Product slice

The previous Help attempt reparented the truthful capability Help dialog into `window.pages` and called `addWidget()`, creating an eighth `QStackedWidget` page while primary navigation has seven routes. The real 11-surface harness correctly rejected that shape.

`b6aaaac…` removes Help from the primary page stack. Help is now a transient `Qt.Widget` child of the existing pATHENA shell, keeps the live capability catalogue, F1 path, focus/accessibility metadata and navigation state, and restores the existing route presentation when hidden. No backend, storage or security semantics changed.

## Exact visual evidence

Windows visual run `34623205385` on exact `b6aaaac…` completed:

- immutable candidate checkout: PASS;
- Ruff: PASS;
- mypy comparator: PASS;
- comparator contracts: PASS;
- shared hierarchy token contract: PASS;
- primary-navigation accessibility contract: PASS;
- capture exactly eleven canonical surfaces: PASS;
- captured workspace route identity: PASS;
- comparison/proposal: PASS;
- artifact upload: PASS;
- final fail-closed visual verdict: FAIL because no approved committed visual baseline exists.

Artifact `pathena-visual-b6aaaac887535bfcafa7e5784d0dc0b590758f36` is exact-SHA bound. All eleven runtime PNGs were downloaded and opened directly. All eleven canonical reference images were also opened directly.

The structural regression is therefore fixed: 11/11 capture now proceeds. The visual Help result is still a `GAP`: `10-help.png` fills the shell rectangle and hides persistent topbar/rail/context, whereas the canonical Help reference keeps shell chrome, a Help sub-navigation column, central capability presentation and right shortcuts/status.

Strict accounting remains `PAIRS_VERIFIED_0_OF_11 · MATCH_0_OF_11`; most reference states are populated/healthy while exact runtime states are empty/reconnecting/unavailable, and there is no same-state Light render for slot 10.

## Test note

The focused Help contract is updated to assert the corrected invariant: `window.pages.count() == window.navigation.count() == 7`, opening Help does not change the current primary page/route, the transient surface belongs to the shell, and hiding it restores the route title. This test change is in the same follow-up candidate as the evidence docs. Do not claim focused PASS until exact CI completes for that candidate.

## Branch / readiness

Run-start Develop is one CI-only commit ahead of the worker merge-base. The current product change does not touch CI/backend/storage/security paths, but the worker is not declared Integrator-ready until compatible Develop baseline and exact focused/canonical evidence are current.

## Next bounded visual slice

Stay on Help only. Preserve the fixed seven-page invariant and real capability content, but move the transient host from the full shell rectangle into the central workspace body so the persistent pATHENA chrome remains visible. Re-run focused Qt/UI tests and exact Windows 11-surface capture; open all eleven AFTER images. Do not start ComfyUI, PALLAS or Command Palette integration before that Help comparison is complete.
