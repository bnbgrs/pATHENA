# Core Focused Candidate — selector/environment repair

Date: 2026-09-14
Owner: Integrator / CI maintenance
Branch: `manual/core-focused-selector-environment-fix-20260914`
Stacked parent at creation: `manual/core-claim-inspection-composition-fix-20260914@4aa966616a0e29d059b3c243556414a0c4a1d5b0`

## Reproduced failure

Exact UI worker head `postmerge/ui@ec05db2214680cbfb4c5112d7b42c24e389c7ea6` triggered Core Focused run `34816284890` because the candidate contains a legitimate Knowledge-owned change.

The focused artifact showed:

- Ruff: PASS;
- focused pytest: no Core-owned changed test selected;
- mypy: FAIL with many PySide6 import errors from unrelated changed UI tests.

Root cause: Ruff/mypy/remediation selected every changed `tests/unit/*.py` whenever the Core workflow was triggered, while pytest already selected only the declared Core-owned families. The environment also installed only `--extra dev`, even though an existing Core-owned selected test, `tests/unit/test_knowledge_review_ui.py`, imports PySide6 directly.

This produced a false Core red on mixed UI/Knowledge candidates and could also make a legitimate Knowledge Qt contract fail because the Focused environment omitted its declared desktop dependency.

## Repair

`.github/workflows/core-focused-candidate.yml` now:

1. keeps the existing trigger families and exact-SHA identity checks;
2. restricts Ruff, mypy and Ruff-remediation Python selection to:
   - `src/athena/knowledge/**`;
   - `src/athena/api/knowledge_*.py`;
   - `test_claim*`;
   - `test_knowledge*`;
   - `test_concept_note*`;
   - `test_identity_transition*`;
   - `test_temporal*`;
   - `test_user_correction*`;
3. installs the existing locked `desktop` extra in addition to `dev`;
4. executes focused Ruff/mypy/pytest/remediation through the same locked dev+desktop environment;
5. sets `QT_QPA_PLATFORM=offscreen` for Qt-backed Knowledge contracts.

`tests/unit/test_core_focused_candidate_workflow.py` locks these boundaries so the broad `tests/unit/.*` selector cannot silently return.

## Non-goals / safety

- No Core product contract is weakened.
- No test family is removed from focused pytest.
- No ignore, Skip or XFail is added.
- No mypy/Ruff rule is disabled.
- No active UI product file is changed.
- No canonical Quality gate behavior is relaxed.

## Integration rule

This branch is intentionally stacked on the Claim-inspection recovery candidate so it can be verified while Develop is red. Do not merge it before the parent recovery is integrated and Develop is canonical-green. After the parent merge, re-check the PR diff/base identity and obtain current exact-head evidence before integration.
