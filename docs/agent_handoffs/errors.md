# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA: `66a8953629a7bce28e19479c9309a016c62ee63a`
- Worker branch: `postmerge/errors`
- History-preserving NON-FORCE synchronization merge: `cc0f1af855712a5aaee3e9fbeb63b1f653322a47`.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0008`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0007`.
- BLOCKED: none.

## ERR-0008 — Settings runtime/comprehension harness contract mismatch

- Original failing candidate: `5a77a4841dfdda120afaefccb698319d31a7d9e9`.
- First UI correction: `f7da16e05aa50da9ca17e5069a8880a84e34432e` installs `apply_ui_refinements_5001_5100(window)` before accessing the comprehension controller.
- Exact corrected Quality `33845743958` nevertheless completed `failure`: Windows path safety, Linux storage, local-install smoke, validator, Ruff and mypy PASS; only pytest and canonical enforcement FAIL.
- Canonical diagnostics from `33845743958` show one exact failure at `tests/unit/test_pathena_settings_runtime.py:215`: expected substring `Internet-access state is not inferred`, actual `Local Core · connected. Local loopback connection only; this status does not indicate Internet access.`
- `SettingsComprehensionController._sync_local_connection_boundary()` intentionally emits that actual wording whenever `pathenaNetworkScope == "loopback-only"`. In this test the local Core remains `ok` while only the model provider is unavailable, so `loopback-only` remains the truthful state.
- Root cause is therefore finalized as a stale harness text expectation after the first setup-order correction, not a product runtime defect. The minimal UI-owned fix is to keep the accessibility assertion but assert the truthful loopback-specific wording for this state; do not weaken the Internet/non-inference invariant.
- Current synchronized UI head `e6cb967c354f55a1cbb4ca1a4bbd2ff26b863b90` repeated the same pytest-only failure pattern in Quality `33849890354`, so ERR-0008 remains `IN_PROGRESS`.

## Collision avoidance

- UI still owns `tests/unit/test_pathena_settings_runtime.py` and the associated Settings comprehension slice; Error does not introduce a competing product/test mutation while that owner lineage is active.
- Error supplied an exact assertion line, expected/actual strings, runtime state (`loopback-only`) and implementation branch to make the owner correction deterministic.
- Error synchronized NON-FORCE with current Develop and mutated only its canonical ledger/handoff documentation.
- No skip/XFail, assertion removal, security/storage/recovery/Windows guard weakening, force update, main mutation or history rewrite occurred.

## Integrator handoff

- Do not integrate/declare globally green either `f7da16e05aa50da9ca17e5069a8880a84e34432e` or synchronized UI head `e6cb967c354f55a1cbb4ca1a4bbd2ff26b863b90` while their canonical pytest is red.
- UI correction signature: `tests/unit/test_pathena_settings_runtime.py:215` must reflect the existing `loopback-only` accessibility contract (`does not indicate Internet access`) rather than requiring the generic non-loopback phrase (`Internet-access state is not inferred`). Keep the assertion substantive.
- Close ERR-0008 only after a new exact UI SHA passes the focused settings-runtime test, Ruff/mypy, full pytest and canonical enforcement.
- ERR-0001 through ERR-0007 remain cleared.

## Next scan

1. Consume the next UI owner commit after `e6cb967c354f55a1cbb4ca1a4bbd2ff26b863b90` and verify that line 215 is corrected without assertion/guard weakening.
2. Require real canonical Quality completion before moving ERR-0008 to `FIXED`.
3. If UI does not correct it through a complete additional worker cycle and the branch is no longer actively colliding, Error may take the minimal harness-only correction on `postmerge/errors`.
4. Then continue Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt/Desktop lifecycle and local install/start scanning; allocate `ERR-0009` only on concrete reproducible primary evidence.
