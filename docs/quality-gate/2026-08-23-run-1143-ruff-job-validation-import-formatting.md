# Quality Gate #1143 — Ruff I001 in job validation tests

## Scope

Repository: `bnbgrs/pATHENA`

Branch: `agent/pathena`

Observed branch head: `d82fa56244326e1b26260ae970e7625d3a4a9b5d`

Workflow run: `32635891111` (`ATHENA Quality Gate` run #1143)

Job: `97185479727` (`Python 3.12 quality`)

Earlier observations in the same evolving failure family:

- run #1129 / `32635757128`: one I001 in `test_job_builtin_payload_validation.py`;
- run #1133 / `32635811732`: two I001s after `test_job_source_extract_payload_validation.py` was added;
- run #1143: three I001s after `test_job_service_scalar_validation.py` was added.

## Gate decomposition

The run completed repository checkout, Python 3.12 setup, pinned resolver installation, desktop runtime library installation, and `uv lock --check` successfully.

The specification validator then completed with `63/63 PASS`.

Ruff stopped the quality script before mypy and pytest. Therefore run #1143 provides no mypy or pytest result for this head; those phases are downstream-masked, not failures.

## Primary failures

Ruff `0.15.22` reported exactly three `I001` diagnostics, all marked automatically fixable:

1. `tests/unit/test_job_builtin_payload_validation.py:1:1`
2. `tests/unit/test_job_service_scalar_validation.py:1:1`
3. `tests/unit/test_job_source_extract_payload_validation.py:1:1`

No production module was reported by Ruff in this run.

## Root-cause classification

Classification: **test-source import formatting / import-block boundary formatting**, introduced incrementally by parallel job-validation test additions.

The first and third files use an otherwise ordered import block followed by two blank lines before module-level fixture constants. This repository has already observed the same Ruff I001 boundary behavior in Quality Gate #1087: Ruff's import organizer expects a single blank line when an import block is followed directly by a module assignment.

`test_job_service_scalar_validation.py` has the same two-blank-line import-to-constant boundary and also contains a long multi-name `from athena.jobs.service import ...` statement that must be normalized to Ruff's canonical form rather than manually guessed.

## Safety / concurrency

The branch is being updated by parallel agents. Any correction must re-read the current remote head and each affected file immediately before mutation, retain unrelated concurrent edits, and use normal non-force commits only.

`bnbgrs/ATHENA` is outside scope and must remain untouched.

## Verification state

- Dependency lock: **PASS** (`uv lock --check`).
- Specification validator: **PASS** (`63/63`).
- Ruff: **FAIL** (three I001 diagnostics above).
- mypy: **NOT EXECUTED** because Ruff failed first.
- pytest: **NOT EXECUTED** because Ruff failed first.

A follow-up Quality Gate after canonicalizing the three affected test import blocks is required to prove the fixes and expose the next independent gate result.
