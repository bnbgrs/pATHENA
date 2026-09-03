# pATHENA Backend & Systems Handoff

## Baseline

- Shared development baseline: `develop/pathena-next`
- Baseline SHA: `fc3f6e44fcbeecdf1f4e817a4b9523a5ba2fbbaf`
- Worker branch: `postmerge/backend`
- Worker was synchronized NON-FORCE with the shared development baseline before product mutation.
- Error worker state checked from the integrated handoff: no OPEN/IN_PROGRESS ERR IDs and no product/test file ownership collision for this slice.

## Selected backend slice

Area: resource policy / scheduler admission boundary.

Spec/backlog anchor: `docs/agent_backend_run_201_300.md` task 289 records that `ResourceManager.set_mode()` used `mode.value` without first requiring an actual `ResourceMode`.

The current development baseline re-read confirmed the finding: `set_mode(self, mode: ResourceMode)` called `self.chat.ensure_local_user()` and then persisted `mode.value` without a runtime enum guard.

## Product contract

`ResourceManager.set_mode()` is a mutation boundary for persisted scheduler/resource policy. It must accept only an actual `ResourceMode`; malformed runtime values must be rejected before actor creation or database mutation. Valid enum behavior and persisted values remain unchanged.

## Implemented slice

Product commit: `881d662958b9fe6b94a9ad549a72d91abb24e692`

Changes:

- `src/athena/resources/manager.py`: fail-fast `isinstance(mode, ResourceMode)` guard before `ensure_local_user()` and the write transaction.
- `tests/unit/test_resource_mode_boundary.py`: focused regression for malformed runtime values (`"quiet"`, `None`, `True`, arbitrary object) and all real `ResourceMode` values.

Independent diff inspection against the synchronized worker base reports exactly:

- `src/athena/resources/manager.py`: +2 / -0
- `tests/unit/test_resource_mode_boundary.py`: new focused test file

No unrelated production changes are present in the slice.

## Verification state

- Current `develop/pathena-next` SHA rechecked immediately before mutation: unchanged at `fc3f6e44fcbeecdf1f4e817a4b9523a5ba2fbbaf`.
- Static call-chain review: PASS.
- Minimal-diff review: PASS (production diff is exactly two added guard lines).
- Focused pytest runtime: NOT EXECUTED in this run because no local repository/runtime executor was available.
- Canonical Quality on worker SHA: NOT EXECUTED. `.github/workflows/quality.yml` triggers only on `main` push or pull request, so pushing `postmerge/backend` does not create a Quality run.
- Therefore this product commit is **IMPLEMENTED_PENDING_VERIFY**, not yet `READY` for integration under the integrator's focused-test rule.

No PASS claim is made for pytest, Ruff, mypy, or canonical Quality on this worker SHA.

## Safety / recovery impact

The change is fail-fast and side-effect reducing. Invalid values now fail before local-user creation and before persisted resource-policy mutation. Valid resource-mode persistence, admission thresholds, durable jobs, storage, recovery, network policy, Windows path safety, and provider behavior are otherwise unchanged.

No retry, cancellation, recovery, or cross-platform behavior is broadened.

## Platform impact

Platform-neutral Python runtime type boundary. No expected Windows/Linux divergence.

## Integrator handoff

Do **not** integrate `881d662958b9fe6b94a9ad549a72d91abb24e692` yet solely from static evidence. It is the exact minimal candidate and should be promoted once focused runtime evidence confirms:

1. malformed modes raise `TypeError` before `ensure_local_user()`,
2. the persisted policy is unchanged after rejected values,
3. every real `ResourceMode` still persists and round-trips,
4. the existing resource-manager regression set remains green.

If the integrator has an executor capable of running the focused tests on this exact SHA, it may perform that verification before integration. Otherwise leave the candidate pending for the next backend run with executable test access.

## Next backend slice

Do not broaden task 289 while its runtime verification is pending. If no executor is available next run, continue read-only tracing of the next independent residual backend findings without colliding with this candidate:

1. deletion ledger runtime boundary validation (`entity_type`, timestamps, commit sequence, read cursor),
2. external gateway input boundaries (`purpose`, allowed hosts, TTL, max_bytes, finite timeout),
3. then fresh Alpha/Beta/backend gap tracing.
