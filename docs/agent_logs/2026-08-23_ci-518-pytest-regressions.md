# CI #518 — multiple pytest regressions after lint/type gates pass

- First observed: 2026-08-23 00:45 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- Tested pATHENA HEAD: `fa98b6aa8cafc2f169dbf01c91b9af3e318c59c1`
- Current HEAD before log creation: `7b764ab9f90f2bf69ab383a6b8f56f0b77cfe08e`
- GitHub Actions run: `32602427831` / #518
- Job: `97102644559` — `Python 3.12 quality`
- Step: `Run ATHENA quality gate`
- Classification: `OPEN / MULTIPLE TEST REGRESSIONS — root causes require per-cluster analysis`
- Status: `OPEN`

## Gate evidence before pytest

The run proves the earlier lint defect is gone:

```text
TOTAL 63/63 PASS
All checks passed!
Success: no issues found in 234 source files
============================= test session starts ==============================
platform linux -- Python 3.12.14, pytest-9.1.1, pluggy-1.6.0
collected 1453 items
```

Interpretation:

- specification validator: `PASS` (`63/63`)
- Ruff: `PASS`
- mypy: `PASS` (`234 source files`)
- pytest: `FAILURES OBSERVED`, but the workflow was cancelled before pytest emitted its final failure summary/tracebacks

## Observed failing test clusters

The live pytest progress stream showed failures in at least these files before cancellation:

```text
tests/unit/test_desktop_grounded_chat.py FFFFF....
tests/unit/test_pathena_durable_grounded_processing_run_binding.py F
tests/unit/test_pathena_durable_grounded_provider_boundary.py FFF
tests/unit/test_pathena_durable_grounded_provider_hook.py FF
tests/unit/test_pathena_durable_grounded_run_terminal_semantics.py FF
tests/unit/test_pathena_durable_grounded_snapshot_fence.py F
tests/unit/test_pathena_grounded_assistant_context_identity.py F
tests/unit/test_pathena_grounded_assistant_identity_boundary.py FF
tests/unit/test_pathena_grounded_assistant_run_provenance.py .FF.
tests/unit/test_pathena_grounded_completion_context_identity.py FF
tests/unit/test_pathena_grounded_completion_run_fence.py FFFF
tests/unit/test_pathena_grounded_context_package.py .....F.
tests/unit/test_pathena_grounded_coordinator_context_fences.py FF
tests/unit/test_pathena_grounded_processing_run_recovery.py F
tests/unit/test_pathena_grounded_provider_attempt_claim.py FF
tests/unit/test_pathena_grounded_provider_claim_context.py F.F
tests/unit/test_pathena_grounded_provider_identity_binding.py FFFF
tests/unit/test_pathena_grounded_provider_preflight_fence.py F.
tests/unit/test_pathena_grounded_provider_run_repository_fence.py FF
tests/unit/test_pathena_grounded_reconciliation.py FFFF
tests/unit/test_pathena_grounded_restart_no_replay.py .....F
tests/unit/test_pathena_grounded_send_coordinator.py F.FF..F
tests/unit/test_pathena_unified_durable_contract.py ...F
tests/unit/test_pathena_unified_pre_user_recovery.py .FFF
tests/unit/test_pathena_unified_pre_user_restart.py F
tests/unit/test_pathena_unified_pre_user_resume.py F
tests/unit/test_pathena_unified_pre_user_transition.py FF
tests/unit/test_pathena_unified_replay_input.py FFF
tests/unit/test_pathena_unified_send_plan.py FFF.
```

This concentration strongly suggests one or a small number of shared contract/wiring changes rather than dozens of independent defects, but that is only a hypothesis until representative tracebacks and call sites are inspected.

## Cancellation evidence

The job was cancelled at approximately 83% of the suite:

```text
tests/unit/test_protected_source_semantic_schema.py ...                  [ 83%]
##[error]The operation was canceled.
```

Because cancellation occurred before pytest's final report, this run cannot provide exact exception tracebacks for the failed tests. Do not infer individual root causes from the `F` markers alone.

## Fix / mitigation

No production fix applied yet. The next safe approach is to:

1. inspect representative failing tests from the earliest/common clusters;
2. compare their expected constructor/signature/state contracts with current production code;
3. identify the smallest common regression;
4. log a narrower root cause before mutating production code;
5. add/update targeted regression coverage and only then apply the minimal fix.

## Verification evidence

- `PASS`: spec validator, Ruff, mypy in CI #518.
- `FAIL`: multiple pytest tests visibly failed in the progress stream.
- `NOT AVAILABLE`: final pytest summary and tracebacks, because GitHub cancelled the job at ~83%.

## Next action

Start with `test_desktop_grounded_chat.py` and the durable-grounded/provider clusters because they fail early and may reveal a common API/constructor contract shift. If separate root causes emerge, split them into dedicated durable logs rather than treating this file as one monolithic defect.
