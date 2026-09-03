# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA: `3347f766651a9b6e2a03235eca4add7905ad4527`
- Stable read-only parent: `main@0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Worker was fast-forward synchronized NON-FORCE to exact current Develop before mutation.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY:
  - `ERR-0003` P1 — two stale `test_pathena_window.py` assertions still require a permanently visible Workspace inspector even though integrated `UI-GAP-0002` intentionally makes Evidence & Activity context-sensitive. Harness correction: `ebcf0dc2a305e946aabd0309c95316d29a1ebd91`.
- FIXED:
  - `ERR-0001` P2 — deletion-ledger malformed runtime boundary acceptance; product fix `780d25d74ce2e310b6a4bc434f547a23163e8b78`.
  - `ERR-0002` P2 — Ruff I001 deletion-boundary harness regression; fix `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- BLOCKED: none.

## Current evidence

- Backend canonical Quality run `33755878184` on `a4768d9b0ea57a1161c93f603a5101c28b555276` is now completed `failure`.
- Canonical jobs/checks: specification validator PASS; Ruff PASS; mypy PASS; Windows path safety PASS; Linux storage regressions PASS; Local install smoke PASS. Only `Quality — pytest` failed.
- Downloaded diagnostics artifact `9894914799`: exactly `2 failed, 4488 passed, 3 skipped, 2 warnings`.
- Failing tests:
  - `tests/unit/test_pathena_window.py::test_reference_body_directly_owns_workspace_and_persistent_inspector`
  - `tests/unit/test_pathena_window.py::test_reference_inspector_is_persistent_and_composer_action_is_compact`
- Both fail only because `inspector.isHidden()` is true on Workspace without grounded context.
- Failing Backend lineage and current Develop share the exact same product blob `src/athena/desktop/pathena_window.py@b683903cc6e6a1a99950bba168e6e314df545ca1` and stale test blob `tests/unit/test_pathena_window.py@950f868e2e396bab5711bda147a124458c69cc34`; therefore this is a current-baseline error, not stale evidence.
- `docs/ui/VISUAL_GAP_LEDGER.md` explicitly records `UI-GAP-0002` as FIXED: the inspector must be context-sensitive rather than permanently visible. Exact corrected UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` passed canonical Quality run `33745885426`.
- Error-worker fix `ebcf0dc2...` changes only the two obsolete shell test names/assertions and adds a non-Workspace visibility assertion. Product code is untouched.
- Focused execution on the corrected Error head has not been observed: local clone/test was blocked by DNS resolution of `github.com`, and no Error-branch workflow run is currently available. Do not mark ERR-0003 FIXED yet.

## Collision avoidance

- Active Error-worker files: `tests/unit/test_pathena_window.py`, `docs/agent_logs/ERROR_LEDGER.md`, `docs/agent_handoffs/errors.md`.
- UI should avoid parallel edits to `tests/unit/test_pathena_window.py` until ERR-0003 is verified or rejected.
- Product UI files are not owned by Error for this root cause; no mutation to `src/athena/desktop/pathena_window.py` is required.
- Core/Backend are non-overlapping.

## Fix commits

- `ERR-0003` harness candidate: `ebcf0dc2a305e946aabd0309c95316d29a1ebd91`.
- Ledger update: `34e6dc5ef6b7e684f73b2305b7b894f85cd60acd`.

## Integrator-ready commits

None yet for ERR-0003. Verification is still required before integration.

## Blocked root causes

None. Test execution is temporarily unavailable in this worker environment, but the correction itself is committed and reviewable.

## Next scan / verification

1. Run `tests/unit/test_pathena_window.py` and `tests/unit/test_pathena_ui_presentation.py` on the exact current Error head.
2. If green, run the smallest relevant Qt/Desktop regression set; update ERR-0003 to `FIXED` and hand `ebcf0dc2...` to Integrator.
3. Treat the Qt stderr deleted-`QProcess` lifecycle noise from the canonical diagnostics as a warning signal only; allocate a separate ERR-ID only if it becomes a reproducible test/runtime failure.
4. Continue scanning Packaging, Provider/Transport, Research/Jobs, Windows publication/path safety, Storage/Recovery and install/start for new current-lineage signatures.
