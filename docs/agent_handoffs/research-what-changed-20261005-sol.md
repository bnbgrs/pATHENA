# Handoff — Research “What changed” — 2026-10-05

## Baseline

- Repository: `bnbgrs/pATHENA`
- Base: `develop/pathena-next` @ `6732e6a5e798d9cbc782e83d6d26c55c1c0a6d5b`
- Branch: `desktop/research-what-changed-20261005-sol`
- Issue: #296 — “what changed since last research” diff over comparable persisted runs

## Existing durable substrate

`ResearchComparisonService` already provides deterministic comparison over immutable persisted ResearchResults. It:
- accepts a result/scope/job UUID;
- finds the newest earlier completed run with the same stable comparison key;
- fails closed on incomparable explicit pairs;
- diffs exact persisted findings/contradictions and evidence Source IDs;
- reports baseline/current coverage, summaries, uncertainty, snapshot commits and model signatures;
- performs no model call or semantic-equivalence inference.

The service is constructed by `AthenaApplication` but was not consumed by the Desktop.

## Implemented

### Desktop helper process

Adds `research_cli compare-previous <job-id>`.
It calls only `app.research_comparison.compare_previous(job_id)`.

Output is exactly one machine-verifiable line:
- `RESEARCH_COMPARE <json>`

When no earlier comparable run exists, the payload is explicit:
- `available: false`
- exact comparison mode
- exact requested current job ID

No fake empty delta is invented.

### Process-boundary validation

Adds `ResearchComparisonReceipt` and strict parser validation:
- exact comparison mode;
- exact current job identity;
- canonical result/job/source/model UUIDs;
- non-negative snapshot commits;
- finite 0..1 coverage;
- persisted summary/uncertainty text;
- boolean change flags;
- typed added/removed finding/contradiction lists;
- canonical added/removed source IDs.

Exit code 0 alone is insufficient: malformed or mismatched receipts are rejected before UI projection.

### Research Workspace

Adds **WHAT CHANGED**:
- enabled only for a selected `completed` Research run;
- disabled while another Research helper operation is active;
- explains disabled/available state through tooltip/accessibility metadata;
- runs through the existing non-blocking QProcess boundary;
- preserves background-selection ownership semantics.

Verified result rendering shows only persisted comparison facts:
- query;
- baseline/current Job IDs;
- baseline/current Result IDs;
- snapshot commit sequence;
- coverage change;
- model-signature IDs;
- old/new summary;
- old/new uncertainty;
- summary/uncertainty/model-signature changed flags;
- exact added/removed findings;
- exact added/removed contradictions;
- exact added/removed Source IDs.

If no prior comparable run exists, the details pane explicitly states that no earlier run matches the same query/mode/stable filters/coverage target/synthesis pipeline.

## Tests

- strict valid/mismatched comparison receipt binding;
- explicit unavailable state without synthetic changes;
- completed-only compare-button gating;
- exact persisted delta rendering;
- no-prior-comparable empty state;
- CLI helper emits the exact service payload;
- CLI parser recognizes `compare-previous`.

## Scope boundaries

- No model inference.
- No fuzzy semantic diff.
- No second Research index.
- No comparison of incomplete runs.
- No arbitrary user-selected baseline UI in this slice; the service supports it, but #296 asks “since last research”, so Desktop uses deterministic `compare_previous`.
- Splitter persistence is deliberately separate.

## Integration

This branch was prepared while #488/#489 were still awaiting runners. Before PR creation, rebuild/retarget onto the then-current `develop/pathena-next` if Develop advances. Require exact-head Quality and UI-focused validation before checking the #296 Research-diff box.
