# pATHENA Error Hunter Handoff

## Current exact state

- Develop: `72ab7085f40afa74c0334b698dffc3462665d366`; canonical Quality `34779068839` is `IN_PROGRESS`; validator/Ruff/mypy, Linux Storage, Windows release guards and Local Install/pypdf are already green, full pytest still running.
- Error worker: `7d8cab5a231353b9ca2ba3e47ad22a91f2afea9f`; canonical `34778491220 = FAILURE`, but the bounded `ERR-0059` regression passes on this exact SHA.
- Spec/Core: `97bb3c13d6c6a1911b631f0b9d511d0c10c5cc71`; Core Focused `34777239256 = SUCCESS`, canonical `34777239238 = SUCCESS`.
- Backend: `7516c67e1c19fded96239639aa2182c65b236b69`; Backend Focused `34774634769 = SUCCESS`, canonical `34774634757 = SUCCESS`.
- UI: `b3066df5be557047c59331476ea1de4e79045e67`; UI Focused/canonical green; Visual `34770817654 = FAILURE` only at final verdict because reviewed Windows baseline evidence is absent.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — ERR-0059 exact verification consumed

Status: `FIXED`.

Bounded implementation remains commit `ed1ea5c9aadcb06f1b71e5ae9eec2173080a7e72` and is present in exact worker SHA `7d8cab5...`:

- `captured_reference_surfaces = [capture["label"] for capture in captures]`;
- `captured_reference_count = len(captures)`;
- `assigned_reference_count = 11` unchanged;
- PASS remains `not errors and len(captures) == expected_capture_count`;
- post-capture mismatch/error guard unchanged.

Canonical run `34778491220` executed `tests/qa/test_visual_capture_manifest_truth.py` and it passed. Therefore the actual manifest root cause is exact-SHA verified and closed.

Do not modify `ERR-0059` again unless a new exact-SHA manifest-truth regression appears.

## ITERATION-2 — Error-worker canonical red deduplicated

The same exact canonical run is globally red for one unrelated pytest only:

`tests/unit/test_pathena_window.py::test_reference_composer_uses_large_work_surface_and_send_target`

The stale Error-worker baseline renders the Send button at 48px while the retained contract asserts 44px. This is an inherited historical UI geometry state, not a manifest regression. Current Develop source has `composer_action_size = 44`, so do not reopen or re-fix the old geometry root cause on `postmerge/errors`.

The exact Error-worker run has green Specification Validator, Ruff, mypy, Windows release guards, Linux Storage and Local Install/pypdf.

## ITERATION-3 — current green workers

Spec/Core `97bb3c13...` is exact Core-Focused and canonical green. Backend `7516c67e...` is exact Backend-Focused and canonical green. Per green-stays-green, neither is a diagnosis target.

## ITERATION-4 — ERR-0054 ownership

Status: `OPEN`, UI/Visual-review-owned.

Current UI exact SHA remains `b3066df5...`. Its visual run reaches all eleven captures, route identity, compare/proposal and artifact upload, then fails only at final visual verdict. No current evidence proves that all eleven authoritative reference/render pairs have been manually reviewed and approved.

Error worker must not generate, accept or commit a baseline. UI/Visual owner must review the eleven real pairs, then run exact-SHA Visual Regression after any reviewed baseline commit.

## ITERATION-5 — Develop candidate

Current Develop exact SHA is `72ab7085...`. Canonical `34779068839` is already running; no competing run may be started and no diagnosis is authoritative until it terminates. Current completed jobs/steps are green except the still-running full pytest.

## Integrator handoff

`ERR-0059` implementation is bounded to the actual-capture manifest derivation plus its regression guard. It is now exact-SHA verified on the Error worker. Integration may carry only the bounded manifest/test slice; do not import the stale Error-worker UI geometry or broad branch history.

`ERR-0054` remains UI/Visual review only. No automatic baseline acceptance.

## Next root cause

1. Consume terminal Develop canonical `34779068839`.
2. If green, do not reopen Develop/Core/Backend/UI canonical clusters without new exact failure evidence.
3. If red, isolate only the new current exact-SHA root cause and deduplicate cascades.
4. Keep `ERR-0054` with UI/Visual Review and do not revisit fixed `ERR-0059` without a new regression.
