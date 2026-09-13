# Open boundary issues current-Develop handoff — 2026-09-12

## Current status — HISTORICAL / DO NOT RE-PORT

This handoff described the pre-integration state of issues #92, #93, #95 and #96. It is retained for provenance only.

Requalification on 2026-09-13 established that the boundary implementation is already present in current `develop/pathena-next@305703362d539ed467dec27cbc7300a495b3ca03`, representative owned blobs are byte-identical to the verified candidate, current Develop canonical Quality `34726544110` is green, and GitHub issues #92/#93/#95/#96 are already closed with state reason `completed`.

Do **not** create another port, merge the historical candidate, reopen these issues, or schedule worker work from the older wording below unless a new current exact-SHA reproducer establishes a distinct regression.

The remainder of this document is the historical handoff as it existed before that integration was recognized.

## Exact lineage

- Source Develop at branch creation: `develop/pathena-next@cec77b6f8b64ec0bdf29cb546d8db4e1cf16ae80`.
- Isolated Integrator branch: `manual/open-boundaries-current-20260912`.
- Product/test/workflow port commit: `02558f94c0819f3c726b2c4cd62331bebe5a8ab9`.
- `main`, `bnbgrs/ATHENA`, and every `postmerge/*` worker branch remain untouched.

## Purpose — historical wording

The repository still has exactly four open GitHub issues that describe concrete boundary/evidence defects: #92, #93, #95 and #96. Their fixes were already implemented and validated on older isolated candidates, but those candidates were never integrated into Develop and have since drifted behind the current branch.

This branch ports the previously verified blobs onto the current Develop tree without redesigning the fixes.

## Issue #92 — specification-validator repository containment

Ported behavior:

- Markdown scan candidates must resolve inside the repository real-path boundary;
- direct validator reads are guarded by the same containment rule;
- relative Markdown destinations that resolve outside the repository fail closed;
- resolution errors/symlink loops fail closed;
- repository-local symlinks whose final target stays inside the repository remain permitted.

Owned files:

- `scripts/validate_spec.py`
- `tests/unit/test_validate_spec_links.py`
- `tests/unit/test_validate_spec_read_boundary.py`
- `tests/unit/test_validate_spec_scan_containment.py`

Provenance: the equivalent combined boundary candidate was part of PR #106, whose exact canonical Quality run `34650077750` succeeded.

## Issue #96 — Windows portable OutputRoot destructive boundary

Ported behavior:

- caller-controlled `OutputRoot` is validated before any recursive cleanup;
- filesystem roots, repository root/ancestors, unsafe repository-internal targets, unrelated existing directories/files and reparse/junction chains fail closed;
- fresh external custom output is permitted only through the bounded policy;
- repeat custom output requires the pATHENA packaging ownership marker;
- the default managed portable output remains supported.

Owned files:

- `scripts/build_windows_portable.ps1`
- `scripts/windows_packaging_safety.ps1`
- `tests/unit/test_windows_packaging_contract.py`

Provenance: equivalent behavior was in PR #106 and its canonical-green exact head.

## Issue #93 — Windows junction/reparse runtime aliases

Ported behavior:

- the shared repository/runtime boundary checks the existing Windows path chain for junction/reparse traversal;
- ambiguous physical aliasing fails closed before ordinary lexical containment is trusted;
- native tests cover ordinary outside runtime roots, repository descendants, an outside junction alias into the repository, and a repository checkout itself reached through a junction.

Owned files:

- `scripts/windows_common.ps1`
- `tests/unit/test_windows_runtime_root_boundary.py`

## Issue #95 — execute the supported Windows diagnostic wrapper in CI

Ported behavior:

- additive `windows-runtime-boundary.yml` runs on `windows-latest`;
- proves exact candidate checkout;
- runs native runtime-root regressions;
- executes `scripts/check_windows.ps1` itself with locked dependencies and an outside-repository SmokeRoot;
- preserves the canonical Windows path/storage lane rather than replacing it.

The final older Windows candidate also normalizes valid `uv 0.11.21 (...)` build-metadata output so the wrapper does not reject the pinned executable spuriously.

Owned files:

- `.github/workflows/windows-runtime-boundary.yml`
- `scripts/check_windows.ps1`
- `tests/unit/test_windows_check_script_contract.py`
- `scripts/windows_common.ps1`
- `tests/unit/test_windows_runtime_root_boundary.py`

Provenance: dedicated native Windows run `34651538082@158ad7313b5363daaf13d1321862c55f1ad26d26` succeeded on the final older candidate.

## Historical bot coordination rules

1. Treat this branch as the current integration candidate for issues #92/#93/#95/#96. Do not independently copy the same old PR #94/#97/#102/#106/#108 changes into active worker branches.
2. Do not close the issues from provenance alone. Require current exact-head canonical Quality and native Windows runtime/wrapper success, then actual Develop integration and exact integrated verification.
3. Do not weaken path containment, reparse/junction detection, packaging ownership, destructive-cleanup ordering or validator fail-closed behavior to make CI green.
4. No Skip/XFail, test deletion, fake-success workflow paths, force-push or worker-history rewrite.
5. If current Develop advances, compare all owned paths before integration. Recreate/rebase the bounded port if any overlap appears.
6. Old PRs #94/#97/#102/#106/#108 are provenance only once this current candidate is verified and integrated; do not merge equivalent historical candidates again.
7. Keep this boundary branch separate from the current `ERR-0035 / BE-052` Storage repair PR #114 so failures remain attributable.

## Historical required evidence

Before integration:

- canonical specification validator SUCCESS;
- canonical Ruff SUCCESS;
- canonical mypy SUCCESS;
- canonical full pytest SUCCESS;
- canonical Windows path safety SUCCESS;
- canonical Linux storage SUCCESS;
- local install smoke SUCCESS;
- dedicated native Windows runtime/wrapper SUCCESS;
- current Develop/worker collision refresh.

After integration, verify the exact Develop SHA before closing #92/#93/#95/#96.
