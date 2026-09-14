# Manual local-quality reproducibility handoff — 2026-09-14

## Exact lineage

- Integration target: `develop/pathena-next`.
- Exact base: `1530c1e8f17f53a6cbfbda7b7c53b8ee50afe2b5`.
- Base canonical Quality: `34785279278 = SUCCESS`.
- Isolated branch: `manual/local-quality-current-20260914`.
- `main` and `bnbgrs/ATHENA` remain untouched and read-only.

## Problem

`scripts/quality.py` said it mirrored GitHub Actions but still executed the specification validator, Ruff, mypy and pytest with the caller's ambient `sys.executable`. That allowed local results to depend on an unrelated Python environment rather than the repository lock.

The script also ran pytest as one process. Current canonical `.github/workflows/quality.yml` deliberately executes `tests/unit/test_desktop_api_controller.py` in its own interpreter and runs the remaining suite with that module ignored, because PySide owns process-global native state. A local PASS therefore did not reproduce the current canonical Python quality plan.

An older bounded candidate in PR #89 established the locked-uv direction, but its pytest plan predates the current controller isolation. This branch ports the intent onto the current exact Develop contract instead of copying that historical candidate unchanged.

## Bounded repair

Owned paths:

- `scripts/quality.py`
- `tests/unit/test_quality_gate_config.py`
- `tests/unit/test_quality_script.py`
- `tests/unit/test_local_quality_runner.py`
- `docs/agent_handoffs/manual-local-quality-current-20260914.md`

The local runner now:

- starts with `uv lock --check`;
- runs every Python quality command through `uv run --locked --extra dev --extra desktop`;
- anchors every subprocess to the repository root derived from the script location;
- defaults `QT_QPA_PLATFORM` to `offscreen` while preserving an explicit caller override;
- mirrors the current canonical pytest split: isolated Desktop API controller first, then the remaining suite with that module ignored;
- retains default fail-fast behavior and explicit `--keep-going` behavior;
- adds `--dry-run` for a side-effect-free exact command-plan inspection;
- fails closed with exit 127 when `uv` cannot start rather than falling back to ambient Python.

The new contract test reads `.github/workflows/quality.yml` and requires every local command to remain present in the canonical workflow, so future command drift becomes an explicit test failure.

## Collision review

The exact base and current worker deltas were refreshed before mutation.

- Backend `postmerge/backend@e4e1244e8482ac7d78e557ded5f91252cccc0347` has the same tree as current Develop and no product delta.
- Spec/Core current delta is limited to its handoff plus Merge/Split policy and tests.
- Errors current delta is limited to its handoff/ledger plus visual-capture manifest repair paths.
- UI current delta is Desktop/UI/visual-evidence scoped.

None of those deltas touches the five paths owned here. This branch does not modify `.github/workflows/quality.yml`, product runtime code, Storage, Security, UI, Core, Scheduler, provider code or worker handoffs.

## Verification contract

No local full-suite PASS is claimed from the connector-only execution environment. The branch is intentionally prepared for exact-head GitHub verification.

Required before integration:

1. canonical Specification Validator PASS;
2. canonical Ruff PASS;
3. canonical mypy PASS;
4. canonical full pytest PASS, including isolated Desktop API controller execution;
5. Linux Storage PASS;
6. Windows release-guard lane PASS;
7. Local install smoke PASS;
8. fresh Develop/worker collision check if any relevant branch advances.

Do not weaken tests, remove the controller isolation, restore ambient `sys.executable`, add Skip/XFail, or change canonical workflow guards to make this slice pass.

## Bot consumption

This is an Integrator/maintenance slice, not a new product feature. Workers should not independently recreate PR #89 or mutate these paths while this exact candidate is under verification. If canonical CI exposes an owned failure in these five paths, repair it on this isolated branch and document the exact cause. If failure is inherited or belongs to another worker, leave that ownership boundary intact.
