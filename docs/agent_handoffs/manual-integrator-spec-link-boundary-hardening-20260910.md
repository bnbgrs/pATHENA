# Manual Integrator handoff — spec link boundary hardening — 2026-09-10

## Status

IMPLEMENTED -> FOCUSED LOGIC VERIFIED -> CANONICAL EXACT-HEAD QUALITY REQUIRED

This is a bounded manual Integrator/maintenance slice. It is not a new worker lane and must not absorb Backend, Errors, Spec/Core, UI, Storage/WAL, Research, Desktop, Quality-workflow, promotion, or local-quality ownership.

## Branch and exact base

- Branch: `manual/integrator-spec-link-boundary-hardening-20260910`
- Exact base: `develop/pathena-next@3330a0092eaddf58fd3a4fdcb7128f77f01b0301`
- Base commit: `ci(windows): exercise adaptive chat reserve contract`
- `main` is untouched.
- Develop is not mutated directly by this slice.

## Why this slice exists

The canonical specification validator scans repository Markdown and validates relative Markdown link targets. Before this slice it resolved each relative target with `Path.resolve()` and then checked only whether the resulting path existed.

That was a fail-open trust-boundary gap. A target such as `../../outside.md` could resolve to an existing file outside the repository and be accepted. A symlink located inside the repository could likewise resolve to an existing external file and be accepted. In both cases the validator would report that relative Markdown links resolve even though the linked content was outside the repository tree being validated.

The issue is especially relevant to a local-first, auditable project: canonical specification validation should prove properties of the repository candidate, not silently depend on arbitrary host files outside that candidate.

## Implementation

Owned code adds `resolve_repository_link()` to `scripts/validate_spec.py`.

The helper:

- resolves the repository root;
- resolves the real target path;
- uses `Path.relative_to()` against the resolved repository root;
- returns `None` when the real target escapes the repository;
- otherwise returns the resolved repository-local destination.

The existing Markdown link scan now reports escaped targets as broken with an explicit `(outside repository root)` diagnostic. Existing missing-target behavior remains separate: a repository-local destination is returned normally and the pre-existing `destination.exists()` check decides whether it is broken.

This deliberately does not change Markdown parsing, fragment handling, external HTTP/HTTPS/mailto handling, chapter numbering, normative specification rules, filesystem ignore rules, or any Alpha/Beta content.

## Focused tests

A dedicated new test file exists at `tests/unit/test_validate_spec_links.py` because no dedicated validator-link unit-test contract was found on current Develop.

It covers four boundary cases:

1. a normal in-repository relative link is accepted;
2. an existing `../` traversal target outside the repository is rejected;
3. a symlink inside the repository that resolves to an existing file outside the repository is rejected, with an OS-capability skip only when symlink creation is unavailable;
4. a missing but repository-local target still resolves as repository-local so the existing existence check remains responsible for the missing-file failure.

The pure boundary mechanism was exercised locally against all four cases and passed 4/4, including an actual symlink escape on the available host.

No local full-repository pytest, Ruff, mypy, or canonical-quality PASS is claimed here. The container cannot clone GitHub, and canonical GitHub Quality remains the authority for the published exact head.

## Worker collision review

Worker branches were refreshed before branching and again after implementation.

### Backend

Observed latest head during this run: `postmerge/backend@338e4514d144f4701e52515c0196e0f968f5db47`.

Its current delta against Develop contains `.github/workflows/quality.yml`, Core/Application, Desktop/MainWindow, Research Delta, Storage/WAL and associated tests/evidence. It does not contain either owned validator path in this slice.

Decision: no Backend file, Quality workflow, Storage/WAL, Research Delta, Core/Application, dependency, or Desktop/MainWindow file is touched here.

### Errors

Observed latest head during this run: `postmerge/errors@b7933c64c15763cc09b791b422ce0a09a83e9b4d`.

Its current delta against Develop is exactly its Errors handoff and error ledger. Neither is touched here.

### Spec/Core

Observed head: `postmerge/spec-core@b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`.

Its current delta against Develop is its own handoff only. This slice does not edit that handoff and does not change Alpha/Beta specification content.

### UI

Observed head: `postmerge/ui@af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.

Its current delta owns UI handoff/visual ledgers, shared components, MainWindow and UI tests. None is touched here.

## Exact owned paths

Reserve only these paths while this candidate validates:

1. `scripts/validate_spec.py`
2. `tests/unit/test_validate_spec_links.py`
3. `docs/agent_handoffs/manual-integrator-spec-link-boundary-hardening-20260910.md`

No other path belongs to this slice.

## Existing manual Integrator candidates

- PR #88 promotion hardening remains independent and untouched.
- PR #89 local-quality reproducibility is independently canonical-green on exact head `e0f5ec1a8014c354e734f05cc3288abeac4eba04`; it remains unmerged and untouched here.
- PR #90 coordination-guard hardening is independently canonical-green on exact head `924cab12c87800fb465f2c4636594f55f277efcc`; it remains unmerged and untouched here.

Do not combine their evidence with this candidate. A green SHA authorizes only that exact candidate.

## Deliberate non-work

Do not widen this slice into:

- `.github/workflows/quality.yml` or Issue #87;
- Storage, WAL, migrations, checkpointing or database schema work;
- Research Delta or adaptive-context-reserve work;
- `src/athena/desktop/pathena_window.py`, shared UI components or visual ledgers;
- active Backend, Errors, Spec/Core or UI handoffs/ledgers;
- Alpha/Beta normative content;
- `scripts/quality.py` from PR #89;
- promotion-readiness or promotion-guard work from PR #88;
- coordination-guard work from PR #90;
- `main` or direct Develop mutation.

No new workflow wiring is required: `scripts/validate_spec.py` is already executed by canonical Quality. The purpose of this slice is to harden that existing validator boundary, not create another CI lane.

## Bot consumption rules

1. Treat this branch/PR as a bounded validation vehicle, not another autonomous worker.
2. While validation is active, reserve only the three exact owned paths above.
3. Do not duplicate these changes into Backend, Errors, Spec/Core or UI branches.
4. Do not alter Alpha/Beta spec content merely to make a new root-escape failure disappear; first verify whether the link itself is invalid.
5. If canonical CI is red in one of the owned paths, repair only the minimal owned cause.
6. If canonical CI is red outside the owned paths, classify it as inherited, platform, or another worker's evidence before changing anything.
7. Do not touch `.github/workflows/quality.yml` from this candidate. Backend currently owns that path.
8. Do not auto-merge. Before integration, refresh Develop and worker heads and compare these exact owned paths for drift.
9. If this branch is rebased, recreated or amended, old CI evidence does not authorize the new SHA. Obtain fresh exact-head evidence.
10. Keep PRs #88, #89 and #90 independent. Their ownership and exact-SHA evidence must not be collapsed into this candidate.

## Integration criterion

Promotion state for this slice is:

`IMPLEMENTED -> 4/4 BOUNDARY LOGIC PASS -> EXACT-HEAD CANONICAL QUALITY REQUIRED -> FRESH DRIFT REVIEW -> DO NOT AUTO-MERGE`
