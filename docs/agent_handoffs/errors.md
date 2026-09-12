# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@146fb7280dbfe30f2bec129aec8ee77f015ce040`.
- Reconciliation source: `postmerge/errors@e33839260e5582e972aa6e311c9631afbe08fe24`; active Errors branch is not mutated directly.
- Current workers: Spec/Core `a35a67f1afe2789d8a568fa3484ef5fe29f46de9`; Backend `6fcfdf8a71abcabad7e3b4a661ad35ee1f6603f8`; UI `9e9227dc722d7d771ae4ce4e45a75983330fed97`.
- Develop canonical `34697870543@146fb7280dbfe30f2bec129aec8ee77f015ce040 = FAILURE`, isolated to ERR-0042 Ruff; full pytest itself is green (`4982 passed, 17 skipped`).
- Spec/Core current Core Focused `34698818610 = SUCCESS`; canonical `34698818608 = FAILURE` only from inherited ERR-0042, with full pytest `4989 passed, 17 skipped` and all other canonical lanes green.
- Backend current Focused `34700396671 = SUCCESS`; canonical `34700396666` had Spec/Ruff/mypy/Windows/Linux/install green with full pytest running at observation.
- UI current UI Focused `34699977144 = SUCCESS`; Core Focused `34699977166 = FAILURE` from ERR-0043; canonical inherits ERR-0042.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- `ERR-0041 = FIXED_PENDING_VERIFY` — Spec/Core provenance import order repaired on current worker and Core Focused green; final canonical recheck awaits repaired Develop baseline sync.
- `ERR-0042 = IN_PROGRESS` — current Develop release-readiness Ruff baseline; repair PR #121.
- `ERR-0043 = IN_PROGRESS` — Core Focused deleted-file selector / untracked diagnostic-worktree defect; repair PR #122.
- `ERR-0040`, `ERR-0035`, `ERR-0033 = FIXED`.
- `ERR-0038`, `ERR-0039 = STALE`.
- No other top-level current cluster is reproduced at this reconciliation point.

## ERR-0042 — current Develop Ruff baseline

Exact reproducer: `develop/pathena-next@146fb7280dbfe30f2bec129aec8ee77f015ce040`, canonical `34697870543 = FAILURE`.

The failure is exactly two Ruff `I001` import-format errors:

- `src/athena/release_readiness.py:3:1`;
- `tests/unit/test_release_readiness.py:1:1`.

Everything else on that exact Develop SHA is green: specification validator, mypy, Windows Path Safety, Linux Storage Regressions, Local Install Smoke and full pytest (`4982 passed, 17 skipped`). The release-readiness tests themselves pass.

Repair PR #121 is deliberately bounded to the two Ruff-green formatting blobs plus a bot handoff. It does not consume Backend Schedule Recovery. Exact candidate head `22f7b640cccad1a65ccc6a32e46778b47e2a697e`; canonical `34700566097` already has Spec/Ruff/mypy/Windows/Linux/install green while full pytest runs.

Promotion sequence: exact-head #121 canonical SUCCESS -> refresh Develop and worker drift -> merge with expected head -> post-merge canonical SUCCESS on resulting Develop SHA -> mark ERR-0042 FIXED.

## ERR-0043 — Core Focused deleted-file harness defect

Exact reproducer: `postmerge/ui@9e9227dc722d7d771ae4ce4e45a75983330fed97`, Core Focused `34699977166 = FAILURE`.

Root cause is workflow selection, not UI/Core product semantics:

- `git diff --name-only` selected candidate-deleted `src/athena/knowledge/orphan_knowledge.py` and `tests/unit/test_orphan_knowledge.py`;
- Ruff failed `E902 No such file or directory`;
- focused pytest failed `file or directory not found`;
- remediation then failed because its own untracked `.focused-evidence/` made `git status --porcelain` non-empty.

Repair PR #122 updates all three selectors to `--diff-filter=ACMRT`, preserving added/copied/modified/renamed/type-changed candidate coverage while excluding deleted paths. The remediation cleanliness check becomes tracked-only via `--untracked-files=no`, and final dual Ruff+pytest enforcement is unchanged. Static contract tests lock the behavior.

#122 is stacked on #121 only to avoid current Develop ERR-0042 polluting its verification. After #121 integrates, retarget/recreate the bounded #122 delta on current Develop and obtain fresh exact-head evidence before integration.

## ERR-0041 — current Spec/Core repair state

Historical reproducer `23dc4c79f1e44cd099992eb23636b2c95014c790` failed Ruff in `provenance_explanation.py`.

Current `postmerge/spec-core@a35a67f1afe2789d8a568fa3484ef5fe29f46de9` contains the organized standard-library import block. Core Focused `34698818610 = SUCCESS`. Canonical `34698818608` no longer reports the provenance import defect; it fails only on inherited ERR-0042, with specification validator, mypy, full pytest (`4989 passed, 17 skipped`), Windows, Linux storage and local install all green.

Keep ERR-0041 at FIXED_PENDING_VERIFY until Spec/Core is refreshed against the repaired Develop baseline and an exact-current canonical run confirms no recurrence.

## Bot ownership rules

- Backend: continue bounded Schedule Recovery work; do not merge it merely to obtain the two ERR-0042 formatting blobs already isolated in #121.
- Spec/Core: do not patch release-readiness files for inherited ERR-0042; sync after Develop repair. Do not recreate deleted files to work around ERR-0043.
- UI: UI Focused is green; do not change UI product code for inherited ERR-0042 or Core workflow ERR-0043.
- Errors: consume this reconciliation only after rechecking exact current heads; do not mark ERR-0042/0043 FIXED before integrated exact-SHA evidence.
- Integrator: preserve pypdf packaging, frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.
