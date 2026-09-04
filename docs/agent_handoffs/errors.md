# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA: `4d36d5f13e1449973e74c48df5e2efb53d0e8aae`
- Stable read-only parent: `main@0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Worker synchronized history-preservingly and NON-FORCE with exact current Develop via merge commit `ae52fb6243d85219a0328d602212b280f75b02a2`.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0005`.
- FIXED: `ERR-0001`, `ERR-0002`, `ERR-0003`, `ERR-0004`.
- BLOCKED: none.

## New exact evidence

### ERR-0005 — system-tray QApplication ownership typing

Canonical UI Quality run `33822842314` failed on exact SHA `19402585415e7b5ed341386bb2d689d6a636e270`. Windows path safety, Linux storage, local-install smoke, specification validator, Ruff and full pytest passed; the only primary failing step was `Quality — mypy`. Canonical enforcement failed downstream because mypy was red.

UI correction `72e43bc18c28b5c92f6528919abf788f66924ba9` is bounded to `src/athena/desktop/pathena_system_tray.py`. It keeps the existing runtime ownership guard but performs type narrowing before assigning the instance attribute: `application = app or QApplication.instance()`, fail if that value is not a `QApplication`, then assign `self.app: QApplication = application`.

Exact-head follow-up Quality run `33822861477` has already passed specification validator, Ruff and mypy, plus Windows path safety, Linux storage and local-install smoke. Full pytest/canonical enforcement are still running. Therefore the issue is `FIXED_PENDING_VERIFY`, not `FIXED`.

## Collision avoidance

- No Error-owned product/test mutation was required; UI already owns and supplied the minimal root-cause correction.
- Error mutated only its canonical ledger/handoff and synchronized NON-FORCE with Develop.
- Backend/Core remain untouched.

## Integrator handoff

- Reject exact failing UI SHA `19402585415e7b5ed341386bb2d689d6a636e270`.
- Do not treat `ERR-0005` as closed until exact-head UI Quality `33822861477` completes `success` including full pytest and canonical enforcement.
- If that run is fully green, close `ERR-0005` immediately and consider corrected UI lineage `72e43bc18c28b5c92f6528919abf788f66924ba9` independently under normal READY rules.
- `ERR-0001`..`ERR-0004` remain closed; no recurrence is evidenced.

## Next scan / verification

1. Consume exact completion of UI run `33822861477`; close `ERR-0005` only on full success, otherwise classify any residual primary failing signature before further mutation.
2. Continue Packaging, Provider/Transport, Research/Jobs, Persistenz/Recovery, Qt/Desktop lifecycle and install/start scans.
3. Re-open historical errors only if their exact signatures recur on the then-current Develop SHA.
