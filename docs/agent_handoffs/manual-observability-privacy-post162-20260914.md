# Manual Observability Privacy — post-#162 reconstruction

Date: 2026-09-14
Base: `develop/pathena-next@cbe5854e35f6914cc785a2397718f6faff44eb03`
Source lineage: PR #86 / `independent/observability-privacy-20260909`

## Purpose

Reconstruct the existing B24 structured-log privacy hardening on the current post-#162 Develop baseline without entering Backend/WAL, Spec/Core/Knowledge, Errors, or UI/PALLAS ownership.

## Why this is safe to reconstruct

The two pre-existing owned paths, `src/athena/observability/logging.py` and `tests/unit/test_logging.py`, are byte-identical on current Develop to their state at PR #86's merge-base `24364b858e15fd9e3b06a9ee2eaf1f580b51364c`. Therefore no later Develop changes are being overwritten.

The old exact-head Quality run `34388567198` had Ruff, mypy, Linux storage, Windows path safety and local-install smoke green. Full pytest had exactly two failures:

1. `test_delta_research_freezes_only_new_explicit_sources`: inherited Develop gap at the time. Current Develop now explicitly includes `ResearchMode.DELTA` in `ResearchRepository.freeze_local_candidates`, so that historical blocker is already resolved outside this candidate.
2. `test_json_formatter_handles_escaped_quotes_in_quoted_sensitive_values`: the formatter output showed the sensitive values correctly redacted, but the test asserted that substring `word` was absent from the entire encoded JSON. That substring necessarily occurs in the key `password`. This reconstruction removes only that invalid substring assertion while preserving direct assertions that the password and prompt fields are fully redacted.

## Product behavior restored

- recursively redact secret-bearing structured fields;
- redact authorization, cookies, API keys, passwords, secrets, credentials and tokens in textual forms;
- redact sensitive URL query values/userinfo and remove URL fragments while preserving safe context;
- redact OAuth-style URL query `code`, `state`, `key`, `nonce` without globally hiding normal diagnostic fields with those names;
- sanitize logging format arguments before interpolation so arbitrary argument `__str__` / `repr` is not invoked;
- stop blind unknown-object stringification and emit only safe type markers;
- preserve UUID/datetime structure and safe byte-length metadata;
- bound cycles/depth and non-finite floats;
- retain exception type plus basename/line/function while omitting exception message and full local paths;
- rebind the owned ATHENA console handler to current `sys.stderr` without accumulating handlers;
- enforce no-semantic-payload-by-default for prompts, knowledge bodies, model outputs, source chunks and request/response content;
- add `component` as a backward-compatible alias of logger name while preserving `logger`;
- retain producer-supplied correlation/event metadata without fabricating IDs.

## Files

- `src/athena/observability/logging.py`
- `tests/unit/test_logging.py`
- `tests/unit/test_observability_logging_privacy.py`
- this handoff

## Integration rule

Fresh exact-head canonical ATHENA Quality is mandatory. Keep draft and do not auto-merge. Recheck Develop head and worker collisions immediately before integration. This slice does not implement persistent JSONL rotation/retention or cross-layer request/job/model-run correlation; those remain separate composition work.