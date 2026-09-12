# Manual Integrator handoff — coordination guard hardening — 2026-09-10

## Status

IMPLEMENTED -> FOCUSED VERIFIED -> CANONICAL QUALITY PENDING

This is a bounded manual Integrator/maintenance slice. It is not a new worker lane and it must not absorb unrelated Backend, Errors, Spec/Core, UI, Observability, Storage, WAL, packaging, promotion, or local-quality work.

## Branch and base

- Branch: `manual/integrator-coordination-guard-hardening-20260910`
- Exact branch base: `develop/pathena-next@38586782fd9b615ecd4226a4b0afe674d5520978`
- Base commit: `ci(packaging): verify pypdf metadata on Windows`
- Base was independently canonical-green before this slice was created.

## Collision / ownership review

Worker diffs were refreshed against Develop before editing.

### Backend

Observed head: `postmerge/backend@a5e28d3c9d3f215620fe69a7dfa9e024155037cf`.

Backend currently owns a broad Storage/WAL delta plus `.github/workflows/quality.yml`, `pyproject.toml`, Core/Storage tests, and part of `src/athena/desktop/pathena_window.py` / MainWindow testing.

Decision: no Storage, WAL, Quality workflow, dependency, Core runtime, or Desktop-window file is touched here.

### Errors

Observed head during the run: `postmerge/errors@df3f63e0c0c717f0bbd8a4388535c5cd645e83ee`.

Its current delta against Develop is documentation-only (`docs/agent_handoffs/errors.md` and the Integrator error ledger).

Decision: do not edit either Errors-owned document.

### Spec/Core

Observed head: `postmerge/spec-core@b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`.

Its current delta against Develop is documentation-only (`docs/agent_handoffs/core.md`).

Decision: do not edit the Core handoff or opportunistically take Core product work.

### UI

Observed head: `postmerge/ui@af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.

UI currently owns bounded Desktop/UI product and test files, including `pathena_window.py`, MainWindow, Jobs/Sources workspace tests, UI lifecycle/theme coverage, and visual evidence.

Decision: no UI/Desktop file is touched here.

### Existing manual Integrator slices

- PR #88 / `manual/integrator-promotion-hardening-20260910` owns promotion-readiness and promotion-guard paths. Exact head is independently canonical-green. Untouched here.
- PR #89 / `manual/integrator-local-quality-repro-20260910` owns `scripts/quality.py`, three local-quality test files, and its own handoff. Untouched here; its corrected exact-head CI remains separate evidence.

## Owned paths — reserve exactly these while this candidate validates

1. `scripts/coordination_guard.py`
2. `tests/unit/test_coordination_guard.py`
3. `docs/agent_handoffs/manual-integrator-coordination-guard-hardening-20260910.md`

No other path is part of this slice.

## Why this slice exists

`coordination_guard.py` was introduced as a fail-closed mutation-coverage guard and later hardened so malformed ledger arrays fail cleanly. Its current candidate-diff parser still had topology gaps that could make incomplete evidence look valid:

1. A commit could contain `"paths": []`. The coverage loops then had nothing to inspect, so the commit could contribute no checked path and still avoid an error.
2. A path entry could be an empty/blank string. The parser required only a JSON string, not a meaningful path.
3. `base_sha != candidate_sha` could be supplied with an empty `commits` array. That claims the candidate advanced while providing no commit evidence to inspect.
4. With non-empty commits, `candidate_sha` was not required to equal the last supplied commit SHA. A diff could therefore claim head X while the guard only inspected commits ending at Y.
5. A diff could contain commits while `base_sha == candidate_sha`, which is internally contradictory for a candidate-delta artifact.

The last three are especially important for multi-agent coordination: path coverage is only trustworthy when the supplied commit sequence actually reaches the candidate being authorized.

## Implementation

### Candidate paths now fail closed

Candidate commit paths are parsed by `_path_tuple()` instead of a permissive generic string-array helper.

The parser now requires:

- a JSON array;
- at least one path per supplied commit;
- every path to be a non-blank string.

This deliberately does not invent filesystem normalization, glob semantics, or path rewriting. Existing exact/prefix claim matching remains unchanged.

### Candidate topology is now internally consistent

After parsing commit entries:

- if `commits` is empty, `candidate_sha` must equal `base_sha`;
- if commits are present, `candidate_sha` must differ from `base_sha`;
- when commits are present, the final supplied commit SHA must equal `candidate_sha`.

This does not attempt to prove Git parentage offline. It only makes the JSON evidence self-consistent and prevents the guard from authorizing a candidate that is not the candidate actually represented by its supplied commit list.

### Existing coordination semantics retained

No change was made to:

- active `CLAIMED` path coverage;
- exact-commit `COMPLETED` coverage;
- coordination metadata allowlist;
- non-product evidence allowlist;
- stale-ledger detection;
- the rule preventing a ledger already at the candidate SHA from also presenting commits;
- exact/prefix claim path matching.

## Test work

The repository already contained `tests/unit/test_coordination_guard.py`. It was preserved and extended rather than replaced by a second test contract.

Existing tests were updated only where their fixtures previously used a deliberately arbitrary `candidate_sha` unrelated to the last supplied commit. The helper now derives the normal candidate SHA from the final commit and permits an explicit candidate override for negative topology tests.

New focused regressions cover:

1. commit with empty path array -> FAIL;
2. commit with blank path -> FAIL;
3. changed candidate with no commits -> FAIL;
4. candidate SHA different from final supplied commit -> FAIL;
5. commits present without advancing beyond base -> FAIL.

Existing coverage remains for:

- active claim coverage;
- matching completed-claim coverage;
- a single uncovered product path;
- stale ledger SHA;
- candidate already recorded in ledger;
- bounded coordination metadata and non-product evidence classifications;
- attempts to hide product files under non-product classifications;
- old completed claims not authorizing later commits;
- malformed candidate diff;
- malformed `claims` / `completed` ledger arrays.

## Focused local evidence

The exact proposed Guard + test surface was materialized in an isolated local test directory and executed before repository publication.

- `python -m py_compile scripts/coordination_guard.py tests/unit/test_coordination_guard.py`: PASS
- `pytest -q tests/unit/test_coordination_guard.py`: `18 passed`
- test file lines over repository 100-column target: 0
- one >100-character line remains in the Guard, but it is pre-existing code in a diagnostic message and is outside Ruff's configured selected E-rules; this slice does not churn it cosmetically.

No local Ruff/mypy PASS is claimed from an environment that does not have the repository's exact locked developer toolchain. Canonical GitHub Quality remains authoritative.

## Deliberate non-work

Do not use this PR as justification to widen scope into any of the following:

- `.github/workflows/quality.yml` or Issue #87;
- `.github/workflows/promotion-readiness.yml` / promotion guard work from PR #88;
- `scripts/quality.py` or local quality-runner tests from PR #89;
- Storage/WAL, DB, migration, checkpoint, repository, or transaction code;
- `src/athena/desktop/pathena_window.py` or current UI/Desktop worker files;
- active Backend / Errors / Core / UI handoffs or ledgers;
- Observability/model-provider/privacy work;
- `main` or direct Develop mutation.

The coordination guard is not wired into a new workflow in this slice. Workflow adoption is a separate integration decision and would require a fresh ownership/collision review.

## Bot consumption rules

1. Treat this branch/PR as a bounded validation vehicle, not as a sixth worker.
2. While canonical validation is active, reserve only the three owned paths listed above.
3. Do not duplicate these edits into Backend, Errors, Spec/Core, UI, PR #88, or PR #89.
4. If canonical CI fails in one of the three owned paths, repair only the minimal owned cause and update this handoff with the exact failing run/head.
5. If canonical CI fails outside these paths, classify it as inherited/platform/other-worker evidence before changing anything. Do not widen this slice just to make unrelated red disappear.
6. Do not weaken the topology checks to preserve an old fixture. Candidate evidence must represent the candidate it claims to authorize.
7. Do not add workflow wiring merely because this Guard is now better tested. That requires explicit current ownership review.
8. Do not auto-merge. Before integration, refresh Develop and all active worker heads, compare the three owned paths for drift, and use exact-head canonical Quality as the authority.
9. If the branch is rebased or recreated, the old exact-head CI evidence no longer authorizes the new SHA. Obtain fresh evidence.
10. Keep PR #88 and PR #89 independent. Their evidence and ownership must not be collapsed into this candidate.

## Promotion state

Current state at handoff creation:

`IMPLEMENTED -> 18/18 FOCUSED PASS -> CANONICAL EXACT-HEAD QUALITY REQUIRED -> DO NOT AUTO-MERGE`
