# Independent ContextPackage schema-boundary run — 2026-08-26

## Frozen base and collision policy

This run was frozen on candidate `b9097454965bafd410aac85245bc25eed473d034` and executed on isolated branch `bot/independent-context-schema-boundaries-20260826`.

Before mutation, current open PRs and the candidate were checked. The run deliberately avoided UI/Qt, screenshot harness ownership, TASK-0017 durable filesystem work, TASK-0047 Storage/Core API/Desktop health, TASK-0051 LM Studio transport, TASK-0054 Settings navigation, workflows, scheduler, API, storage product code and Research models.

Only the existing ContextPackage structured-output boundary plus a new focused test file are product/test scope.

## CSB-001 — strict structured-schema JSON contract

Status: **FIXED on isolated branch**.

Fresh current-candidate reproduction/audit showed two asymmetric boundaries:

- writer: `build_from_sections()` used `json.dumps(..., allow_nan=False)` but leaked raw `TypeError`/`ValueError` for non-serializable or non-finite schema values;
- reader: `structured_schema()` used default `json.loads()`, which accepts CPython's non-standard `NaN`, `Infinity` and `-Infinity` constants.

Changes:

- added a rejecting `parse_constant` callback to structured-schema decoding;
- translated strict-JSON decode failures to `ContextPackageError`;
- translated schema serialization `TypeError`/`ValueError` to `ContextPackageError`;
- added a runtime text guard for `structured_schema_id` before `.strip()`.

Regression coverage includes valid roundtrip, `NaN`, positive/negative infinity, a non-serializable object and a non-text schema ID.

Product commit: `75db8bf360728abc8c938aadd2d9129ff3485ce5` (subsequently refined by CSB-002).

## CSB-002 — malformed persisted schema metadata fails closed

Status: **FIXED on isolated branch**.

A second audit of the same boundary found that malformed in-memory/persisted ContextPackage state could still escape the package error family:

- `run_snapshot()` asserted that schema JSON existed whenever schema ID existed, allowing a raw `AssertionError` for half-present metadata;
- non-text schema metadata could reach `.encode()`/`json.loads()` and leak `AttributeError`/`TypeError`.

Changes:

- `structured_schema()` explicitly requires both metadata fields to be text after presence consistency is established;
- `run_snapshot()` now validates paired presence and text types instead of using `assert` as runtime validation;
- malformed metadata consistently raises `ContextPackageError`.

Regression coverage includes both half-present orientations and non-text persisted schema JSON through both reader and snapshot paths.

Product refinement commit: `608333715cf55aa6706fc530b5b25f1d840ddd43`.
Test refinement commit: `a45953d927514e39d07e07db95d41ce53195ac6d`.

## Validation and evidence limits

- The original writer behavior is directly implied by `allow_nan=False`: non-finite floats raise `ValueError`; arbitrary objects raise `TypeError`.
- Default Python `json.loads()` accepts `NaN`/`Infinity`; the new `parse_constant` path rejects them before they enter schema state.
- The source diff was reviewed after mutation; no unrelated product path is intentionally changed.
- The final source rewrite restores the terminal newline that the first contents-API rewrite had removed.
- PR #22 was opened as the authoritative CI carrier, but no PR workflow run materialized for the observed head updates. Therefore **no full Quality PASS is claimed**.

## Queue / agent implications

1. Do not recreate the previously documented structured-schema follow-up: CSB-001/002 supersede it once integrated.
2. Keep old BE-021 and storage-regex queue text treated as stale unless current-head evidence reproduces it; those were handled by the preceding independent run.
3. Do not infer anything about Research Models from this work; that old item remains evidence-blocked unless fresh mypy output exists.
4. Active UI, storage, security and model-transport agents can continue normally; this slice does not occupy their files.
5. If later CI finds a failure attributable to this run, reopen only `src/athena/retrieval/context_package.py` and `tests/unit/test_context_package_schema_boundaries.py` first.

## Files in intended final diff

- `src/athena/retrieval/context_package.py`
- `tests/unit/test_context_package_schema_boundaries.py`
- `docs/agent_logs/2026-08-26-independent-context-schema-boundaries-run.md`
