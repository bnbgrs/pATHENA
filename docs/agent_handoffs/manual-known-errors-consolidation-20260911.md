# Known-error consolidation handoff — 2026-09-11

## Exact lineage

- Source Develop: `develop/pathena-next@e008e0fbf595da64bea64eb557dddeb2cd78bed0`
- Consolidation branch: `manual/known-errors-consolidation-20260911`
- Initial consolidated product commit: `da9d7d0c9ebd65b0ca50fae36180940d6746dd3d`
- This branch is Integrator-owned and isolated. It does not rewrite or mutate `postmerge/backend`, `postmerge/spec-core`, `postmerge/errors`, `postmerge/ui`, `main`, or `bnbgrs/ATHENA`.

## Purpose

Put all currently implemented known-error repairs on one current-Develop lineage so cross-slice interactions are tested together instead of inferred from historical worker heads.

The canonical Error Ledger still names three OPEN top-level errors: `ERR-0033`, `ERR-0035`, `ERR-0039`. This consolidation contains the bounded implementation candidates for `ERR-0033` and `ERR-0035`. `ERR-0039` remains a separate Spec/Core candidate until exact Ruff 0.15.22 remediation is known and verified; this branch only carries the correction to the Ruff remediation evidence workflow itself.

## Included known-error repairs

### Boundary and Windows defects — provenance PR #106

Ported unchanged from the exact candidate whose canonical Quality run `34650077750` succeeded:

- explicit `check_windows.ps1 -SmokeRoot` is validated outside the repository before it is forwarded as persistent `--keep-root`;
- portable Windows packaging validates caller-selected `OutputRoot` before recursive cleanup and requires safe ownership semantics;
- spec validation contains scan inputs, direct reads and relative Markdown destinations inside the resolved repository root.

This covers the implementation candidates for issue #92, issue #96 and the SmokeRoot call-site defect.

### Windows physical runtime boundary and native wrapper evidence — provenance PR #108

- existing repository/runtime path chains fail closed on Windows junction/reparse traversal before lexical containment is considered;
- native Windows tests cover normal outside paths, normalized repository descendants, outside junction aliases into the repository and repository roots reached through a junction;
- additive `windows-runtime-boundary.yml` executes the supported `check_windows.ps1` wrapper on `windows-latest`;
- `Get-PathenaUvVersion` normalizes valid pinned `uv 0.11.21 (...)` output instead of rejecting the executable because of optional build metadata.

Dedicated exact-head Windows run `34651538082@158ad7313b5363daaf13d1321862c55f1ad26d26` succeeded before this port. This is the current candidate for issues #93 and #95.

### ERR-0033 / BE-046 — EmergencyReserve identity and physical reclamation

Provenance PR #110.

The reserve no longer relies on close-then-unlink-by-path as the capacity-release primitive. The already-attested open descriptor is truncated to zero, fsynced and physically re-attested while pathname/object identity is still bound. An empty owned stub remains and can be safely reprovisioned.

Preserved/added invariants:

- non-sparse provisioning;
- parent/root symlink, junction and reparse rejection;
- POSIX root bound to directory descriptor;
- pathname-to-descriptor identity checks around mutation;
- exclusive single-hardlink ownership for an accepted provisioned reserve;
- hardlink insertion detection;
- pre-opened second descriptor cannot keep reserve data blocks allocated after release because the inode itself is truncated;
- unknown physical allocation fails closed;
- Windows physical allocation is queried instead of silently substituting logical length.

At provenance head `15439c84d2e3fb7df3c419ab0bfe5749b23b3bb6`, Ruff, mypy, Linux storage regressions, Windows path/storage gates and local-install smoke were green. Full canonical pytest was still running at the moment this consolidation was created, so this branch must establish fresh current-Develop canonical evidence before `ERR-0033` is called FIXED.

### ERR-0035 / BE-052 — SQLite preflight-to-writer continuity

Provenance PR #109.

`DatabasePreflightReport` now carries a primary DB + WAL + SHM file-set identity. Startup revalidates the exact file-set immediately before writer establishment and rebinds every pre-existing file object after connect before schema/policy mutation. Read-only preflight also detects object replacement while inspection itself is active.

Adversarial tests cover:

- WAL injection after read-only preflight but before writer open;
- primary database replacement at writer establishment;
- file-set snapshot currentness;
- migration-plan synthetic preflight fixtures updated to the identity-bearing report contract.

The first provenance run exposed six old migration-plan test fixtures that omitted `file_set`; those were corrected at `c5f59f28714507de8d1604b79a152549e1d12c7e`. Fresh consolidated Quality is authoritative for closure.

### ERR-0039 support — Ruff remediation evidence workflow

Current Develop's new Ruff remediation step created `.focused-evidence` and then required a completely clean worktree, so its own untracked diagnostics caused the remediation step to fail before `ruff --fix` ran.

This consolidation changes only that diagnostic invariant: cleanliness checks use `git status --porcelain --untracked-files=no`, so tracked candidate mutations remain forbidden while the intentionally untracked evidence directory is ignored. This does not suppress Ruff, change lint rules, auto-commit fixes, weaken focused enforcement or claim ERR-0039 closed.

The actual `tests/unit/test_identity_transition.py` import correction remains on the separate Spec/Core diagnostic path until Ruff's own exact auto-fix diff is captured and verified.

## Bot coordination rules

1. Treat this branch as the integration candidate for the listed Windows/Spec boundary fixes plus ERR-0033 and ERR-0035. Do not independently copy the same repairs into active `postmerge/*` branches while this exact candidate is validating.
2. Do not mark `ERR-0033` or `ERR-0035` FIXED from provenance alone. Require this consolidation's exact-head canonical Quality plus its Linux/Windows storage evidence.
3. Keep `ERR-0039` OPEN until the separate corrected Spec/Core exact SHA has Ruff + focused pytest green and canonical Quality acceptable. The workflow repair here is evidence infrastructure, not the lint fix.
4. Never weaken Storage/Recovery, Windows path, packaging, specification containment, allocation, hardlink, symlink/reparse or fail-closed assertions to make CI green.
5. No Skip/XFail, assertion dilution, test deletion, fake success path, force-push or history rewrite.
6. If a consolidated failure appears, classify it as product regression, test-contract migration, platform semantics or pre-existing baseline before changing code.
7. PR #106/#108/#109/#110 remain provenance. If equivalent code from this consolidation is later integrated, do not merge those historical candidates again.
8. Issues #92/#93/#95/#96 stay open until equivalent code is actually integrated into Develop; green draft evidence alone is not issue closure.
9. Refresh `develop/pathena-next` and all worker heads immediately before any promotion/merge decision.
10. `main` remains read-only unless an explicit later promotion decision authorizes it.

## Promotion evidence required on this exact branch

- specification validator: green;
- Ruff: green;
- mypy: green;
- full pytest: green;
- Linux storage regressions: green;
- Windows path/storage/release guards: green;
- local install smoke: green;
- dedicated native Windows runtime/wrapper gate: green;
- no new current exact-SHA known error introduced by the combined diff.

Only after those conditions are met may the corresponding repaired defects move from implementation candidate to verified closure.