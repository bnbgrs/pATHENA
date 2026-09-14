# Core Focused type-change selector — post-#150 handoff

## Exact lineage

- Base: `develop/pathena-next@b3766e0c690aac4db0567c63a3e2886f8fbce368`.
- Functional commit: `ddb4c4186ec3c58c0917e6d7cedd852d1e8e51b5`.
- Historical provenance: PR #124 originally established that candidate-deleted paths must be excluded while Git type-changed paths remain selected.

## Current regression

The current Core Focused workflow retained `--diff-filter=ACMR` in four selectors. That excludes deleted paths correctly but also drops `T` (type-changed) paths from Ruff, mypy, focused pytest, and Ruff-remediation selection.

## Repair

- all four selectors use `--diff-filter=ACMRT`;
- the current narrow Core-owned test-family selector remains unchanged;
- locked `dev+desktop` environment and `QT_QPA_PLATFORM=offscreen` remain unchanged;
- the workflow contract test requires exactly four `ACMRT` selectors and rejects the regressed `ACMR` form.

No product runtime, lint rule, type rule, test assertion, Skip/XFail, or gate outcome is weakened.

## Integration rule

Open a Draft PR only after post-#150 canonical Quality on base `b3766e0...` is green. Require exact-head Core Focused + canonical Quality before integration. Merge serially before later Core/PALLAS qualification so subsequent candidates use the repaired selector.