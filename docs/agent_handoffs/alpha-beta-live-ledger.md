# Alpha/Beta live integration ledger

OBSERVED_AT_UTC: 2026-10-01T22:19:42Z
DEVELOP_SHA: 8d8097eda3cdc389e721f7077ddad1881b93afbe

| ROLE | PR/BRANCH | EXACT_HEAD | STATUS | GATES | HANDOFF_DOC | OWNER_NEXT |
|---|---|---|---|---|---|---|
| Core / Storage | #325 integration/canonical-commit-bundle-fresh-20261001 | ea6503775d27417358e800abed5dd48faedf3028 | BLOCKED | Storage Focused PASS; Quality FAIL at native PySide chat-selection segfault; non-storage Quality components PASS | docs/agent_handoffs/alpha-beta-canonical-commit-bundle-20261001.md | Core: do not patch Storage; requalify after harness integration |
| UI / Research | #326 ui/research-accessibility-current-20261001 | e7d4fbd7f9d0011121a4d3837a01ca9ff345d848 | READY | UI Focused PASS; 11-Surface Visual PASS; ATHENA Quality PASS | isolated one-file Research port; no role handoff found | Integrator: history-preserving merge when repository mutation is permitted |
| CI / Harness | #327 ci/isolate-chat-selection-qt-20261001 | b30f536f757788f6a99d4dca9a05edc94830ce19 | RUNNING | previous head proved isolated chat-selection module PASS and rest suite 5512 PASS/19 skipped, but two quality-contract tests failed; current head aligns local quality plan and Quality 6320 is running | workflow diff + exact CI evidence | Integrator/CI: update contract tests if still required; require exact-head Quality PASS |
| QA/Core/Runtime cancellation | #328 docs/chat-cancel-handoff-current-20261001 | 46c7f35c49940e1a63f9b6ab064d49eb630a6e9c | RUNNING | documentation-only; Quality 6312 running | docs/agent_handoffs/alpha-beta-chat-cancel-20261001.md | Core/QA/Runtime: reuse handoff; no duplicate analysis |

STALE_EVIDENCE:
- #327 head 77b749f2e46e94654d8c6fea82e0d33ac0d22fc0 is stale after local-quality-plan alignment commit b30f536f757788f6a99d4dca9a05edc94830ce19.
- #324 and #322 are closed/superseded and are not integration candidates.
- Old Runtime/QA/Sources branches without unique delta are ignored.

INTEGRATED_THIS_RUN:
- None. #326 is exact-head green and READY, but the attempted ready/merge mutation was blocked before GitHub changed the PR.

BLOCKERS:
- #327 current exact-head Quality is running. Previous failure was harness-contract drift, not a failed isolated Qt regression.
- #325 must not receive Storage churn for the native PySide failure.
- Chat cancellation remains missing; provider-level bounded abort remains PARTIAL/MISSING.

NEXT_5_INTEGRATION_ACTIONS:
1. Integrate #326 history-preserving once repository mutation is permitted; then distribute new Develop SHA.
2. Finish #327 harness-contract alignment and require exact-current-head Quality PASS; integrate only after that.
3. Requalify #325 on post-harness Develop; require current-head Quality plus Storage Focused PASS and current protected-metadata/ID handoff.
4. Integrate #328 documentation after exact-head Quality if still current/mergeable; use it as the sole cancellation architecture source.
5. Start fresh Core cancel-control-plane, QA acceptance, Runtime provider-abort, and Runtime Update-Preflight slices from the then-current Develop.

MAIN remains read-only.
