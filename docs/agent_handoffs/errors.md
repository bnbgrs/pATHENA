# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA: `7be496d2fcbb94ab81f5e520f2e45ee2820d3fd9`
- Stable read-only parent: `main@0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Worker synchronized history-preservingly and NON-FORCE with exact current Develop before mutation via `0c26f67871c871a39f0ee980aaa4c21a6e6b2892`.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED:
  - `ERR-0001` P2 — deletion-ledger malformed runtime boundary acceptance; product fix `780d25d74ce2e310b6a4bc434f547a23163e8b78`.
  - `ERR-0002` P2 — Ruff I001 deletion-boundary harness regression; fix `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
  - `ERR-0003` P1 — stale persistent-inspector harness contract; verified fix `6253577227d427c9bb00707c3e3e578a16c0f9d6`.
- BLOCKED: none.

## Current evidence

- Backend canonical Quality run `33755878184` on `a4768d9b0ea57a1161c93f603a5101c28b555276` failed only at full pytest with two stale `tests/unit/test_pathena_window.py` assertions; validator, Ruff, mypy, Windows path safety, Linux storage and local-install smoke passed.
- Diagnostics artifact `9894914799`: exactly `2 failed, 4488 passed, 3 skipped, 2 warnings`.
- Product contract is `UI-GAP-0002`: Evidence & Activity is contextual, not permanently visible.
- Initial candidate `ebcf0dc2a305e946aabd0309c95316d29a1ebd91` corrected the failing assertions but did not restore the complete previously verified state-transition coverage.
- Final Error fix `6253577227d427c9bb00707c3e3e578a16c0f9d6` restores the exact canonical-green shell test blob `82f492814250536dd003857a4eec2d083e9e13d5` from UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb`.
- Current Error lineage and canonical-green UI head share byte-identical directly relevant blobs:
  - `src/athena/desktop/pathena_window.py@b683903cc6e6a1a99950bba168e6e314df545ca1`
  - `tests/unit/test_pathena_window.py@82f492814250536dd003857a4eec2d083e9e13d5`
  - `tests/unit/test_pathena_ui_presentation.py@171f209728831feb1ac7bb06172e30aee12973ae`
- Canonical Quality run `33745885426` on exact UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` completed `success`; this is exact-content verification of the affected product and focused harness state.
- Fresh local execution was attempted again but checkout was blocked by DNS resolution of `github.com`; no fabricated separate local PASS is claimed.

## Collision avoidance

- Error-owned active files for this closed root cause: `tests/unit/test_pathena_window.py`, `docs/agent_logs/ERROR_LEDGER.md`, `docs/agent_handoffs/errors.md`.
- Integrator should preserve exact shell-test blob `82f492814250536dd003857a4eec2d083e9e13d5` while integrating ERR-0003.
- UI may resume changes to `tests/unit/test_pathena_window.py` after integration, but should not reintroduce the persistent-inspector contract.
- Product UI code was not changed by Error.
- Core/Backend are non-overlapping.

## Fix commits

- Synchronization merge: `0c26f67871c871a39f0ee980aaa4c21a6e6b2892`.
- `ERR-0003` verified harness fix: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.
- Ledger closure: `05785eb84151eb841519980da94ff3ad02700383`.

## Integrator-ready commits

- READY: `6253577227d427c9bb00707c3e3e578a16c0f9d6` for ERR-0003, after/current with synchronization merge `0c26f67871c871a39f0ee980aaa4c21a6e6b2892`.
- Preserve exact test blob `82f492814250536dd003857a4eec2d083e9e13d5`.
- After integration, run canonical Quality on the resulting exact Develop SHA when available.

## Blocked root causes

None.

## Next scan / verification

1. Continue scanning the Qt deleted-`QProcess` stderr warning; allocate a new ERR-ID only if a current-lineage runtime/test failure is reproducible.
2. Inspect Packaging, Provider/Transport, Research/Jobs, Windows publication/path safety, Storage/Recovery and local install/start for fresh current-lineage signatures.
3. Re-open historical errors only if their exact signatures recur on the then-current Develop SHA.
