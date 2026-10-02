# pATHENA handoff — Core startup rollback on current Develop — 2026-10-02

BASE: develop/pathena-next@3357bf1e66d9d60d7b1c9e2d528c36632d89fbc5
BRANCH: core/startup-rollback-current-20261002-sol
LEGACY_SOURCE: PR #371 @ e0c57e846ee89ff0d15458dffd3f48ae02daec50

## Root cause

AthenaApplication.start() only had transactional cleanup inside ServiceManager.start_all(). Failures after services started could leave lifecycle services alive. configure_logging() also ran after state became STARTING but outside the guarded startup block.

ServiceManager.stop_all() forgot a service even when its stop() raised. That made later cleanup retries incorrectly treat the resource owner as already released.

## Current reconstruction

- logging setup is inside the guarded startup boundary;
- every handled startup failure attempts ServiceManager.stop_all();
- rollback failure is logged without replacing the primary startup exception;
- services whose stop fails remain tracked in original start order for a later retry;
- focused startup rollback and retry regressions are included;
- the two legacy interrupt-boundary tests are corrected to assert retained ownership after failed stop.

## Legacy CI evidence

Old #371 exact head:
- specification validator: PASS
- Ruff: PASS
- mypy: PASS
- Windows path safety: PASS
- Linux storage regressions: PASS
- local install smoke: PASS
- pytest: 5536 passed, 19 skipped, 2 failed

Both failures were stale assertions expecting failed-to-stop services to disappear from ServiceManager. That directly contradicted the new retryable ownership contract. No product exception or crash caused those failures.

## Files

- src/athena/core/application.py
- src/athena/core/services.py
- tests/unit/test_application_startup_rollback.py
- tests/unit/test_service_manager.py
- tests/unit/test_service_manager_interrupt_boundaries.py

## Validation truth

Fresh exact-head CI is required before integration.
