# Manual handoff — Canonical Qt quality isolation — 2026-10-02

## Ausgangslage

Draft PR #327 correctly identified a process-lifetime Qt failure mode in `tests/unit/test_desktop_chat_selection_state.py` and isolated that module in the canonical GitHub Quality workflow. Its exact-head Quality run 36934474207 still failed after the change.

## Root Cause

The isolation change updated only `.github/workflows/quality.yml` and `scripts/quality.py`.

The repository treats the canonical Quality command plan as a tested contract. Three test modules still described the previous six-check plan and single isolated Qt module:

- `tests/unit/test_local_quality_runner.py`
- `tests/unit/test_quality_script.py`
- `tests/unit/test_quality_workflow_contract.py`

That mismatch caused five deterministic failures after 5,509 other tests passed. The multiline remaining-suite command from #327 also made the local-plan-in-workflow assertion impossible to satisfy by exact command text.

## Änderungen

Ported the useful #327 isolation onto fresh `develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728` and completed the canonical contract:

- isolate `test_desktop_api_controller.py` in a fresh interpreter;
- isolate `test_desktop_chat_selection_state.py` in a second fresh interpreter;
- execute the remaining suite exactly once with both modules excluded;
- retain independent exit-code capture for all three pytest invocations;
- mirror exactly the same seven-check plan in `scripts/quality.py`;
- update local runner, script orchestration and workflow contract tests;
- keep the remaining-suite shell command on one line so the local command-plan contract can verify it exactly.

## Dateien

- `.github/workflows/quality.yml`
- `scripts/quality.py`
- `tests/unit/test_local_quality_runner.py`
- `tests/unit/test_quality_script.py`
- `tests/unit/test_quality_workflow_contract.py`

## Verhalten danach

Canonical Quality still runs every test. The two known process-sensitive Qt modules are mandatory, but each runs in a clean interpreter and is excluded only from the final remaining-suite process.

Local `scripts/quality.py` now describes the same command graph, so CI and developer quality execution cannot silently diverge.

## Validierung

The prior #327 failing run provided the concrete reproduction:
- Ruff: PASS
- mypy: PASS
- isolated Desktop API controller: PASS
- isolated Desktop chat-selection test: PASS
- remaining suite: 5 failures, all Quality-contract synchronization failures
- 5,509 other tests passed

This branch corrects each reported contract failure. No local PASS is claimed because this execution environment has GitHub repository access but no runnable pATHENA checkout. Exact-head PR CI is the executable validation source.

## Konfliktrisiko / Parallelität

This branch does not modify #327. It is a fresh current-Develop replacement so the bot's old branch remains untouched.

At synchronization time no other fresh active PR changed these five Quality contract files. The Supervisor/Integrator should prefer this fresh replacement over merging #327 directly if exact-head gates pass.

## Nächste sinnvolle Schritte

1. Require exact-head ATHENA Quality on this branch.
2. If green, integrate this replacement and retire/supersede #327 through the normal integrator workflow.
3. Do not weaken or skip the isolated Qt tests; the purpose is deterministic process isolation, not reduced coverage.
4. If another Qt module proves process-lifetime sensitive later, add it as another explicit mandatory isolated check and update all three contract tests in the same change.

## Branch / base

- Base: `develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`
- Branch: `fix/quality-chat-selection-isolation-20261002`
- Replaces the incomplete #327 approach without mutating its branch.
