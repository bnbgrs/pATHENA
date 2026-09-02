# Quality Gate run 1623 — Ruff primary failures

## Scope

Repository: `bnbgrs/pATHENA`

Observed workflow run: `32641286080` / run number `1623`.

The specification validator completed with `63/63 PASS`. Ruff then failed and the gate stopped before mypy and pytest. Therefore mypy and pytest for this run are **NOT EXECUTED** and must not be inferred.

## Primary failure 1 — snapshot renderer import block

Ruff reported `I001` at `scripts/render_pathena_ui_snapshot.py:1:1`.

Classification: formatting/import-order failure introduced by the new UI snapshot renderer.

The renderer import block was subsequently reformatted on `agent/pathena`; the current file no longer matches the failing block shown by run 1623.

Status: **FIXED ON CURRENT HEAD, CI REVALIDATION REQUIRED**.

## Primary failure 2 — research keyboard-flow zip contract

Ruff reported `B905` at `src/athena/desktop/pathena_research_experience_2500.py:347` for `zip(focus_order, focus_order[1:])` without an explicit `strict=` argument.

Classification: Bugbear explicit-zip-contract failure. The two sequences intentionally differ by one element, so `strict=True` would be incorrect and would raise. The semantically correct fix is `strict=False`.

Current code uses:

```python
for first, second in zip(focus_order, focus_order[1:], strict=False):
```

Status: **FIXED ON CURRENT HEAD, CI REVALIDATION REQUIRED**.

## Primary failure 3 — backup deletion codec test import block

Ruff reported `I001` at `tests/unit/test_backup_deletion_codec_canonicalization.py:1:1`.

Classification: import-order/formatting failure in the test module as checked out by run 1623.

The current branch copy has been re-read after the failing run. A fresh CI run is required to determine whether this historical `I001` still reproduces on the moving head; no PASS is claimed without that run.

Status: **CURRENT SOURCE RE-READ; CI REVALIDATION REQUIRED**.

## CI-structure finding discovered while triaging run 1623

The quality workflow had been changed to render and upload a UI screenshot before invoking `scripts/quality.py`. That allowed a Qt/snapshot failure to mask the actual specification/Ruff/mypy/pytest gate. A dedicated `.github/workflows/ui-snapshot.yml` already exists, so the quality workflow was restored to run the actual quality gate directly after dependency-lock validation.

Fix commit from this triage slice: `ebe3152bddb99307ad6a0618502acd95c2b664c0`.

## Additional concurrent-delta finding

A parallel change in `src/athena/jobs/recovery.py` used an inner `except BaseException: pass` while attempting rollback. That can violate Bugbear policy and would also swallow `KeyboardInterrupt`/`SystemExit` in the secondary rollback path. The inner handler was narrowed to `except Exception` without changing the outer fail-closed re-raise behavior.

Fix commit: `9c9f25fcbef720b65ec027bc5e6366ea5ced925c`.

## Required next gate slice

1. Run/observe the quality workflow on the latest `agent/pathena` head.
2. Confirm specification validator remains green.
3. Confirm Ruff passes the three run-1623 primary failures plus the recovery rollback change.
4. Only after Ruff passes, classify the first mypy failure if any.
5. Only after mypy passes, classify the first pytest failure if any.

No result beyond observed CI output is claimed in this log.
