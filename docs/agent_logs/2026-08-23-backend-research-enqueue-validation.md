# Backend run: Research enqueue persistence hardening

Date: 2026-08-23
Branch: `agent/pathena`
Repository: `bnbgrs/pATHENA`
Scope: backend only

## Production problem

`ResearchService.enqueue_local()` accepted several runtime values that Python treats as numeric even though they are semantically invalid Research configuration. In particular, `bool` is a subclass of `int`, so values such as `context_limit=True`, `time_start_us=True`, or `max_hierarchy_depth=True` could pass the enqueue-time comparisons and be persisted into a durable `research.exhaustive` job. The later persisted-state decoder already rejects booleans, so such a job could become permanently invalid only after it had entered durable storage.

Malformed runtime types could also escape as raw `TypeError` or `AttributeError` before the service boundary normalized them into `ResearchConfigurationError`.

## Changes

`src/athena/research/service.py`

- Reject non-text Research queries before calling `.strip()`.
- Reject boolean and nonnumeric `coverage_target`; normalize accepted values to `float` before persistence.
- Reject boolean/non-integer `time_start_us` and `time_end_us`.
- Reject boolean/non-integer `context_limit`, `output_reserve`, `safety_margin`, and `max_hierarchy_depth`.
- Validate `requested_model_id` before normalization.
- Require domain filters to contain strings, UUID filters to contain `uuid.UUID`, and source-type filters to contain `SourceType` values.
- Preserve the existing canonical persisted representation and existing `initialize()` decoding contract.

No schema migration was required.

## Regression coverage

Added `tests/unit/test_research_enqueue_validation.py` covering:

- boolean numeric fields are rejected before any `research.exhaustive` job is persisted;
- malformed scalar types raise `ResearchConfigurationError` rather than leaking Python implementation exceptions;
- non-text query rejection happens before persistence;
- malformed filter element types are rejected before persistence;
- valid integer coverage is normalized to `1.0`, persists canonically, and can initialize a ResearchScope successfully.

## Validation status

The changed production file and the new test file were re-read from the current `agent/pathena` branch after the commits. A local targeted pytest run could not be started in this automation environment because the execution container cannot resolve `github.com`, so no claim of executed tests is made. CI/Quality-Gate state was intentionally not inspected because it is outside this backend agent's assignment.

## Isolation

This run changed only backend Research service code, backend unit tests, and this backend agent log. It did not modify Qt/UI/UX/Desktop implementation files and did not touch `bnbgrs/ATHENA` or any repository other than `bnbgrs/pATHENA`.
