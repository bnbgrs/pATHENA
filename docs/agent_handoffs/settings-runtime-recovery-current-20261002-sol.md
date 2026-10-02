# pATHENA handoff — Settings runtime recovery on current Develop — 2026-10-02

BASE: develop/pathena-next@3357bf1e66d9d60d7b1c9e2d528c36632d89fbc5
BRANCH: settings/runtime-recovery-current-20261002-sol
LEGACY_SOURCE: PR #333 @ 196768816b52b31629abba6579090fd69552601f

## Safety check

Both branch-owned files on current Develop were byte-identical to #333's original base. PR #419 does not touch these files. The qualified two-file delta was therefore ported unchanged.

## Fixes

- transient initial News profile failure no longer permanently latches the request state;
- News load/save presentation clears stale success/error semantics while work is in flight;
- QSettings read errors are checked before missing model identity can return early;
- Settings model selection hydrates the same persisted per-model controls as Chat selection.

## Legacy evidence

- UI Focused: PASS
- Ruff: PASS
- pytest: PASS
- Windows path safety: PASS
- Linux storage regressions: PASS
- local install smoke: PASS
- Quality failed only because the old base had unrelated mypy errors in api/asgi.py (missing CoreApiSurface enable_news/disable_news methods).
- The old visual run predated the later deterministic PALLAS visual-capture integration.

Fresh exact-head current-Develop Quality/UI/visual evidence is required before merge.
