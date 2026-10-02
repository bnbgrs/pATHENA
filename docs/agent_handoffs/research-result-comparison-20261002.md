# ResearchResult comparison handoff — 2026-10-02

## Ausgangslage

Issue #296 includes a QoL requirement to show what changed since the last
Research run. The durable Research pipeline already persisted immutable
ResearchResults, exact synthesis text, coverage, snapshot commit identity,
model signature identity and finding/contradiction provenance, but there was no
result-to-result comparison path in Core or the desktop.

The existing \`athena.research.delta\` path creates a new Research scope from
explicit new Source IDs. It does not compare two completed persisted
ResearchResults and therefore does not satisfy the review/inspection workflow.

## Root Cause

The data required for an auditable comparison already existed in
\`ResearchPromotionService.result_view()\`, but no read-only domain boundary
selected the prior comparable result or diffed the persisted content. The
desktop therefore had only Result and Promotion actions.

A second root cause was discovered from the concurrent helper-lifecycle work in
PR #353: \`research_results_cli.py\` started the full \`AthenaApplication\`
lifecycle for short-lived read/result/promotion commands. Full Core startup owns
unrelated global services and can perform cross-subsystem writes. PR #353
deliberately left this file to PR #357 to avoid a file conflict.

## Änderungen

### Persisted Research comparison

Added \`ResearchComparisonService\` and \`ResearchResultDelta\`.

The service:

- resolves a current persisted ResearchResult by result, scope or job UUID;
- requires the current and baseline scope to be completed;
- automatically selects the newest earlier completed comparable result;
- treats query, Research mode, stable scope filters, time window, coverage
  target and synthesis pipeline version as the comparability contract;
- intentionally allows the captured/explicit Source set to change, because that
  evidence change is part of the user-visible delta;
- compares exact persisted finding and contradiction text while preserving
  duplicate counts;
- compares exact summary and uncertainty text;
- compares real persisted coverage ratios;
- compares finding/contradiction Source provenance;
- records model-signature changes as a caveat rather than inventing a semantic
  explanation;
- performs no model call and no semantic-equivalence inference.

### Desktop / CLI

Added \`research_results_cli compare <identifier> [--baseline UUID]\`.

Without \`--baseline\`, the command uses the newest earlier comparable completed
result. If there is no prior comparable result, it returns a structured
\`available: false\` payload instead of an error or a fake delta.

The Research result panel now exposes a state-dependent **Compare previous**
action for completed runs. The detail pane renders:

- baseline/current Result and snapshot commit identity;
- real coverage movement;
- added/removed exact finding text;
- added/removed exact contradiction text;
- added/removed persisted Source provenance;
- summary and uncertainty text changes;
- explicit comparison-method disclosure;
- a model-signature-change warning when applicable.

The UI uses explicit \`loading\`, \`ready\`, \`unavailable\`, and \`error\`
comparison states. It does not invent a percentage or success state.

### Helper lifecycle

\`research_results_cli.py\` now starts/stops only
\`app.storage_bootstrap\` around the short-lived command. It no longer starts or
stops the full Core lifecycle. Storage shutdown failure is surfaced as Exit 2
rather than swallowed.

This follows the root-cause work in concurrent PR #353, whose owner explicitly
left \`research_results_cli.py\` to this PR to avoid conflict.

## Dateien

Product:

- \`src/athena/research/comparison.py\`
- \`src/athena/core/application.py\`
- \`src/athena/desktop/research_results_cli.py\`
- \`src/athena/desktop/research_review.py\`
- \`src/athena/desktop/research_results_extension.py\`
- \`src/athena/desktop/pathena_research_result_presentation.py\`

Tests:

- \`tests/unit/test_research_comparison.py\`
- \`tests/unit/test_desktop_research_results_cli.py\`
- \`tests/unit/test_pathena_research_review.py\`
- \`tests/unit/test_pathena_research_result_presentation.py\`
- \`tests/unit/test_application_wiring.py\`

## Verhalten danach

A completed Research run can be inspected and compared with the newest earlier
persisted run that has the same stable Research scope. A missing comparable run
is shown honestly as unavailable. A changed model signature is visible, and
textual changes are explicitly documented as exact persisted text changes, not
as model-decided semantic changes.

Short-lived ResearchResult desktop commands no longer impersonate a second
global Core lifecycle.

## Validierung

Direct local checkout was attempted before implementation but the execution
environment could not resolve \`github.com\`; therefore no local pytest, Ruff or
mypy PASS is claimed.

Performed before exact-head CI:

- current Develop and active PR/file ownership were inspected repeatedly;
- branch was created from
  \`develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b\`;
- schema migration was checked against the comparison SQL
  (\`research_scopes\` / \`research_results\` persisted columns);
- branch/develop diff was reviewed;
- PR mergeability was rechecked after product/test commits;
- focused tests were added for domain comparison, exact duplicate handling,
  incompatible scopes, honest no-baseline state, CLI transport, Qt rendering,
  progressive action visibility, application wiring and helper lifecycle.

Authoritative current-head CI must be read from PR #357. No CI success is
claimed in this handoff until those checks complete.

## Bekannte Restprobleme

- The comparison is intentionally lexical/provenance based. A paraphrase is
  reported as one removal plus one addition.
- It does not compare arbitrary unrelated Research queries; incompatible scopes
  fail closed or are skipped when finding the prior baseline.
- No manual Windows desktop click-through is claimed from this execution
  environment. The PR's Qt-focused and visual workflows are the available
  runtime validation path.
- Universal Search from #296 was investigated but deliberately not implemented
  in this run because the necessary API composition file was already owned by
  the active chat-cancellation PR. That work remains separate.

## Abhängigkeiten / Parallelität

The branch deliberately avoided active lanes for Chat cancellation/API,
Chat branching, Storage, LM Studio runtime, Settings, Sources, Obsidian,
Knowledge selection, Windows packaging and CI workflows.

During the run:

- PR #353 documented the helper-lifecycle root cause and explicitly handed
  \`research_results_cli.py\` to #357. That follow-up is incorporated here.
- PR #358 appeared for Research desktop protocol truth, but its file set is
  \`research_workspace.py\`, \`research_workspace_protocol.py\` and its focused
  test; it is disjoint from this candidate.
- PR #360 appeared for packaged helper routing and is also file-disjoint from
  this candidate.

## Konfliktrisiko

Highest overlap risk for later integrations:

- \`src/athena/core/application.py\`
- \`src/athena/desktop/research_results_cli.py\`
- \`src/athena/desktop/research_results_extension.py\`
- \`src/athena/desktop/research_review.py\`
- \`src/athena/desktop/pathena_research_result_presentation.py\`

Do not replace these files wholesale. Preserve the comparison wiring and the
storage-only helper lifecycle if another branch touches them.

## Nächste sinnvolle Schritte

Integrator / QA:

1. Require exact-head green ATHENA Quality Gate.
2. Require exact-head UI Focused Candidate.
3. Inspect the exact-head visual-regression artifact for the completed Research
   state; the new comparison action must not create clipping or control overlap.
4. Recheck PR #358 and #353 integration order. Their final file sets are
   currently disjoint, but their behavior is adjacent.
5. After integration, exercise two comparable completed Research runs with
   changed Sources and confirm the displayed Source/finding delta matches the
   persisted Result views.
6. Keep Universal Search as a separate #296 slice after the active API/cancel
   ownership clears.

## Branch / Commits / PR

Branch: \`feature/research-result-diff-20261002-sol\`

Commits before this handoff:

- \`bc5d1407da9643e152d77d5f52d1e61b267b3cc6\` —
  \`feat(research): compare persisted result changes\`
- \`91e85fdb175a5b50bbcfd43b11737ac50d303aee\` —
  \`feat(desktop): expose persisted research result comparison\`
- \`38d145a452cc99814572db83d701bc17785558aa\` —
  \`test(research): cover result comparison workflow\`
- \`3c1fb004ce5d2dd11f2d1766602d583bab98a4fd\` —
  \`fix(desktop): isolate ResearchResult helper lifecycle\`

PR: #357 — Research: compare changes across persisted completed results

Tracking issue: #296.
