# Backend & Systems Handoff

Generated: 2026-09-10
Branch: `postmerge/backend`

## Current source of truth

- Develop consumed first: `develop/pathena-next@4046459bf2b91f9d30efee1f9b726c40080e2408`.
- Current Backend worker head before this documentation refresh: `31752aefe0d5f79d8c305c531cc7584c0585e175`.
- Exact Develop canonical Quality `34439530635@4046459bf2b91f9d30efee1f9b726c40080e2408 = FAILURE`, but the failure is isolated to one UI/PALLAS pytest (`tests/unit/test_pathena_pallas_full_view.py::test_open_workspace_reuses_one_synchronized_full_surface`). Ruff, mypy, Windows path safety, Linux storage regressions and local-install smoke are green on the same SHA.
- Exact Backend canonical Quality `34437259339@31752aefe0d5f79d8c305c531cc7584c0585e175 = FAILURE`. Windows path safety, Linux storage regressions and local-install smoke are green; Python Quality is red at Ruff plus 17 pytest failures.

## Closed root-cause cluster — Windows storage bootstrap reserve path

Status: `CLOSED_ON_DEVELOP / EXACT_LANE_VERIFIED`.

The Windows storage-bootstrap failures on Develop `fafbeabdde1207ebc97712aa61ee947410cbf691` shared one harness root cause: `_ReserveStub.ensure()` returned `Path("/tmp/bootstrap-emergency.reserve")`, which is not absolute under Windows. Production `EmergencyReserveStatus` correctly rejected that path fail-closed.

Backend candidate `31752aefe0d5f79d8c305c531cc7584c0585e175` changed only the test stub to a platform-valid absolute path using `Path.cwd() / "bootstrap-emergency.reserve"`. The Windows storage regression lane passed on that exact worker SHA. The bounded correction is now integrated on authoritative Develop as commit `4046459bf2b91f9d30efee1f9b726c40080e2408`, and the exact Develop Windows path-safety job in canonical Quality `34439530635` passes.

No production Storage/Recovery behavior, assertion, fail-closed boundary or workflow command was weakened.

## Current Backend worker red state

Exact diagnostics artifact `10137124325` for `31752aefe0d5f79d8c305c531cc7584c0585e175` reports:

- Ruff: one `I001` import-block formatting failure in `src/athena/storage/schema.py`.
- pytest: `17 failed, 4845 passed, 3 skipped`.
- The pytest failures are concentrated in the worker-only schema-v41 / `research_delta_boundaries` lineage: legacy migration fixtures and stale expected final migration IDs interact with `0041_research_delta_boundary`.

Do not repair those historical fixtures mechanically. Current Develop does not carry the worker-only v41 migration/storage delta, and Integrator explicitly says not to integrate broad Backend/Storage/Migration/Runtime history from this branch. Reconcile worker-only v41/WAL/Storage changes against current Develop/spec contracts before preserving or repairing them.

## Current Develop red state

The exact current Develop pytest failure is UI-owned:

`tests/unit/test_pathena_pallas_full_view.py::test_open_workspace_reuses_one_synchronized_full_surface`

with `AttributeError` on `MessageActionQuietController._containers` during Qt event filtering. This is not a Backend/System root cause and Backend must not mutate UI to make Develop green.

## CI discipline / verification constraints

- No Backend canonical Quality run was queued or in progress when this handoff refresh was prepared; `34437259339` is completed FAILURE.
- The execution container still cannot resolve external package/Git hosts, so pinned Ruff 0.15.22 cannot be installed locally and a fresh focused Ruff run cannot currently be produced here.
- Therefore no speculative Backend product/test mutation follows this documentation refresh. No fabricated focused PASS is claimed.
- Any next Backend mutation must begin with current Develop/worker/run re-check and must have real focused verification before canonical Quality.

## Preserved release guards

- No silent Tor-to-Direct fallback.
- Redirect/Auth/HTTPS/response-size boundaries remain fail-closed.
- WAL maintenance safety remains intact.
- pypdf packaging, Frozen argv and two-EXE topology remain guarded.
- Bounded worker tree and adaptive 2048-context reserve remain guarded.
- Windows lane-lock/path-safety, duplicate-column/Core-startup/storage-bootstrap signatures remain protected and are only OPEN when reproduced on current exact-SHA evidence.
- No Skip/XFail, force push, history rewrite, main mutation, or mutation to `bnbgrs/ATHENA`.

## Integrator prerequisites

- Windows storage bootstrap reserve-path cluster: CLOSED on Develop `4046459bf2b91f9d30efee1f9b726c40080e2408`; no further Backend action required for that slice.
- Broad Backend worker history: HOLD / NOT READY.
- Do not integrate worker-only schema-v41/WAL/Runtime changes without a fresh bounded reconciliation against current Develop and exact focused/canonical evidence.
- Current Develop global red is UI-owned and must not be worked around in Backend.

## Next Backend action

On the next run, consume the then-current Develop and Backend exact-SHA Quality results first. If no current Backend candidate is running, choose the highest still-authoritative Backend/System gap. Prefer reconciliation/removal of obsolete worker-only history over patching fixtures to preserve non-authoritative schema-v41 behavior. Only mutate after real focused verification is available.
