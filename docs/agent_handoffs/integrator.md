# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-11T00:52Z
Branch: `develop/pathena-next`
HEAD at run start: `4634bdf28c98bc114e0369701122818d474f99d9`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads reviewed: Errors `298bbf8ab08a680cb5157651ffa293ce544c62e1`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `44201f9dd2c1378c98afccc9a30ddf18c98b2405`, UI `d55877cd353f7ee598df8213b9508fb143e51e15`.
- Exact Develop canonical Quality `34539454111@4634bdf28c98bc114e0369701122818d474f99d9 = FAILURE`.
- Failure is isolated to `Python 3.12 quality -> Quality — pytest`; specification validator, Ruff, mypy, native Windows path/storage/durable-FS/runtime/ownership/adaptive-reserve/pypdf, Linux storage and Local-install jobs passed.
- Canonical pytest diagnostics report `1 failed, 4830 passed, 3 skipped`: `tests/unit/test_pathena_design_system.py::test_spacing_and_motion_are_small_bounded_scales` still asserted the pre-hierarchy typography tuple `(14, 11, 34)` while the intentionally integrated UI product contract is `(15, 12, 42)`.
- Immediately before this repair mutation, Develop had zero queued and zero in-progress workflow runs.
- `ERROR_LEDGER.md` and `ALPHA_BETA_PROGRESS.md` are not present at repository root on current Develop; no replacement percentages are synthesized.
- Develop visual source of truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md`; neither supports a screenshot-level `MATCH` claim.

## Worker qualification

- Errors current head is documentation-only and hands off SQLite writer-identity and emergency-reserve identity gaps to Backend ownership; no competing Error-owned product slice is integrated.
- Spec/Core has no new product head.
- Backend current head is documentation-only and explicitly does not attribute the current pytest-only failure to Backend product behavior; BE-046 and BE-052 remain open without a bounded verified candidate.
- UI current head is a documentation-only successor to the already integrated typography hierarchy slice. Its next proposed textual top-navigation work is not integrated here because it does not yet have a bounded exact-Develop candidate with focused interaction/accessibility evidence.

## Canonical failure repair

The current canonical failure is a stale duplicate UI test contract introduced by the intentional typography hierarchy promotion. The product values are already covered by the strengthened `tests/unit/test_pathena_design_tokens.py` contract and were the only intended product delta from the preceding canonical-green Develop SHA.

This repair updates only `tests/unit/test_pathena_design_system.py` so its exact typography tuple matches the integrated product contract `(15, 12, 42)`. No assertion is removed or generalized, no Skip/XFail is added, and no product, routing, Storage, Recovery, Security or runtime behavior changes.

The repair is deliberately bounded to the exact failing assertion plus this handoff. Canonical exact-SHA Quality must verify it before any further Develop mutation.

## Persistent release guards

- pypdf packaging remains fail-closed and selected on Linux and Windows canonical lanes.
- Frozen argv and Desktop/Worker two-EXE contracts remain selected in native Windows Quality.
- Exactly one Desktop instance with bounded worker ownership/lifecycle remains guarded.
- Adaptive 2048-context Chat reserve remains selected in native Windows Quality.
- Windows lane-lock/path-safety remains fail-closed.
- Storage-bootstrap, Core-startup and duplicate-column/schema-reinitialization signatures remain selected in Windows Quality.
- Durable filesystem native-Windows behavior remains explicitly tested while POSIX-only identity contracts remain in Linux storage Quality.

## Next integration

1. Consume canonical Quality on the resulting exact Develop SHA first and freeze Develop while it is queued/in progress.
2. If canonical pytest is green, re-qualify current worker heads from fresh exact-SHA evidence; do not absorb documentation-only successors as product slices.
3. Keep the visual verdict fail-closed and do not bless a generated baseline without direct reference/current-render review.
4. Keep Backend-owned BE-046/ERR-0033 and BE-052/ERR-0035 out of parallel Integrator mutation unless a bounded Backend candidate with focused adversarial identity evidence becomes READY.
