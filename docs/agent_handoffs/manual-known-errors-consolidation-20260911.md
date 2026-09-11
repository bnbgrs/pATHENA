# Known-error consolidation handoff — 2026-09-11

## Exact lineage

- Source Develop: `develop/pathena-next@e008e0fbf595da64bea64eb557dddeb2cd78bed0`
- Consolidation branch: `manual/known-errors-consolidation-20260911`
- Initial consolidated product commit: `da9d7d0c9ebd65b0ca50fae36180940d6746dd3d`
- Storage type-closure commit: `ad7f1c08467922d91908d4f1dab1e55393fc6523`
- All-three-ledger-errors product commit: `4d025b108cc7bd39e25c280bcc6b0d2e077b4dbb`
- This branch is Integrator-owned and isolated. It does not rewrite or mutate `postmerge/backend`, `postmerge/spec-core`, `postmerge/errors`, `postmerge/ui`, `main`, or `bnbgrs/ATHENA`.

## Purpose and current error truth

The canonical Error Ledger names three OPEN top-level defects: `ERR-0033`, `ERR-0035`, `ERR-0039`. This consolidation now contains bounded repair implementations for all three on one current-Develop lineage, plus the known Windows/specification boundary repairs from issues #92, #93, #95 and #96.

Do not mark ledger items FIXED merely because their focused repair gates are green. Ledger closure requires exact consolidated promotion evidence. Focused green evidence below means the implementation defect is repaired on its owned surface and is ready for combined qualification.

## Included known-error repairs

### Boundary and Windows defects — provenance PR #106

Ported unchanged from candidate `80b6c095d12da371a1e58dd1b16c0ea72a5566ea`, whose canonical Quality run `34650077750` succeeded:

- explicit `check_windows.ps1 -SmokeRoot` is checked outside the repository before persistent `--keep-root` forwarding;
- portable Windows packaging validates caller-selected `OutputRoot` before recursive cleanup and requires safe ownership semantics;
- spec validation contains scans, direct reads and relative Markdown destinations inside the resolved repository root.

### Windows physical runtime boundary and wrapper execution — provenance PR #108

- existing repository/runtime path chains fail closed on junction/reparse traversal;
- native Windows regressions cover real outside roots, normalized repository descendants, outside junction aliases into the repository and a repository root reached through a junction;
- `.github/workflows/windows-runtime-boundary.yml` executes `check_windows.ps1` itself on `windows-latest`;
- `Get-PathenaUvVersion` accepts pinned `uv 0.11.21` output with optional build metadata while preserving exact semantic version enforcement.

Dedicated provenance run `34651538082@158ad7313b5363daaf13d1321862c55f1ad26d26` succeeded. On the current consolidation before the Core slice was added, exact run `34652771769@ad7f1c08467922d91908d4f1dab1e55393fc6523` also succeeded.

### ERR-0033 / BE-046 — EmergencyReserve identity and physical reclamation

Provenance PR #110.

Release no longer closes the attested reserve and then unlinks a pathname. It reclaims physical capacity through the already-attested open descriptor, verifies identity/allocation and leaves a zero-length owned stub that can be safely reprovisioned.

Preserved/added invariants:

- non-sparse provisioning;
- symlink/junction/reparse ancestor rejection;
- POSIX directory-descriptor binding and pathname-to-descriptor `samestat` checks;
- exclusive single-hardlink ownership for an accepted provisioned reserve;
- hardlink insertion detection;
- a pre-opened second descriptor cannot retain reserve blocks after release because the underlying inode is truncated;
- unknown physical allocation fails closed;
- Windows physical allocation is queried instead of inferred from logical length.

Current consolidated focused Storage run `34652771754@ad7f1c08467922d91908d4f1dab1e55393fc6523` passed Ruff, strict mypy and adversarial storage tests. Linux Storage and native Windows evidence on the same consolidation lineage are also green.

### ERR-0035 / BE-052 — SQLite preflight-to-writer continuity

Provenance PR #109. The same final type fix has also been ported back to that individual PR at `bd2ee0147a51695493a79c711f8e4d71019f5380`.

`DatabasePreflightReport` carries a primary DB + WAL + SHM file-set identity. Startup revalidates the file set immediately before writable connect and rebinds every pre-existing object after connect before schema/policy mutation. Read-only preflight also rejects object replacement during inspection.

Adversarial coverage includes WAL injection after preflight, primary database replacement during writer establishment, file-set currentness and updated migration-plan synthetic fixtures.

The first consolidated strict-mypy run exposed one typing-only defect: `DatabaseFileIdentity.same_object()` accepted `DatabaseFileIdentity` while defensively checking `isinstance`, making the false branch unreachable. The final signature accepts `object` and retains the defensive runtime narrowing. Exact focused Storage run `34652771754` is green after this repair.

### ERR-0039 — Spec/Core Ruff I001 identity-transition candidate

The historical Spec/Core candidate branches were no longer clean current-Develop descendants, so they were not used for promotion evidence. A fresh current-Develop candidate was created as PR #113.

Ruff 0.15.22's own remediation artifact from run `34652701744` produced the exact required diff. The correct import block is:

```python
from uuid import UUID

import pytest

from athena.knowledge.identity_transition import MergeTransition, SplitTransition

A = UUID(...)
```

The important detail is one blank line between the first-party import and the following module constants, not the extra blank line present in the earlier candidate. No `noqa`, rule suppression, skip, XFail or assertion change is used.

PR #113 exact head `98196f25c8c7e0a590e87711f3e54e0308b7f13b` has focused Core run `34652909370 = SUCCESS`: exact Ruff passed, all six identity-transition tests passed, and final fail-closed enforcement passed. Those exact product/test blobs are now included in this consolidation at commit `4d025b108cc7bd39e25c280bcc6b0d2e077b4dbb`.

### Ruff remediation evidence infrastructure

Develop's diagnostic remediation step originally created `.focused-evidence` and then rejected its own untracked directory as a dirty worktree. The consolidation uses `git status --porcelain --untracked-files=no`, so tracked candidate mutation remains forbidden while diagnostic files do not block Ruff's auto-fix evidence. The workflow never auto-commits a fix and focused enforcement remains fail closed.

## Current exact evidence

Already green on the current consolidation lineage before the final ERR-0039 port:

- focused Storage known-error gate `34652771754@ad7f1c08467922d91908d4f1dab1e55393fc6523 = SUCCESS`;
- native Windows runtime/wrapper `34652771769@ad7f1c08467922d91908d4f1dab1e55393fc6523 = SUCCESS`;
- Core focused infrastructure on that lineage = SUCCESS;
- Linux Storage and local-install evidence on the preceding consolidated exact head = SUCCESS.

Independent exact ERR-0039 evidence:

- Core focused `34652909370@98196f25c8c7e0a590e87711f3e54e0308b7f13b = SUCCESS`.

After commit `4d025b108cc7bd39e25c280bcc6b0d2e077b4dbb`, new exact combined Core, Storage, Windows and canonical Quality runs are authoritative. Do not substitute the earlier focused runs for the final combined exact-SHA result when promoting.

## Bot coordination rules

1. Treat this branch as the integration candidate for issues #92/#93/#95/#96 and `ERR-0033`, `ERR-0035`, `ERR-0039`. Do not duplicate these repairs into active `postmerge/*` branches while this exact candidate validates.
2. Keep all three ledger errors OPEN until exact combined evidence meets the Error Ledger's FIXED definition. Focused green means repair-ready, not merged/promoted.
3. Never weaken Storage/Recovery, Windows path, packaging, specification containment, allocation, hardlink, symlink/reparse or lint assertions to make CI green.
4. No Skip/XFail, assertion dilution, test deletion, `noqa`, fake success path, force-push or history rewrite.
5. Classify every new consolidated failure as product regression, test-contract migration, platform semantics, CI infrastructure or pre-existing baseline before changing code.
6. PR #106/#108/#109/#110/#113 remain provenance. If equivalent code from this consolidation is integrated, do not merge those historical candidates again.
7. Old ERR-0039 diagnostic PRs #107 and #111 are superseded by current-Develop PR #113 and must not be used as promotion evidence.
8. Issues #92/#93/#95/#96 stay open until equivalent code is actually integrated into Develop; draft green evidence alone is not issue closure.
9. Refresh `develop/pathena-next` and all worker heads immediately before any promotion decision.
10. `main` remains read-only unless an explicit later promotion decision authorizes it.

## Promotion evidence required on the final exact consolidation SHA

- specification validator: green;
- Ruff: green;
- mypy: green;
- full pytest: green;
- focused Storage known-error gate: green;
- Core focused candidate: green;
- Linux storage regressions: green;
- Windows path/storage/release guards: green;
- local install smoke: green;
- dedicated native Windows runtime/wrapper gate: green;
- no newly reproduced current exact-SHA known error.

Only after those conditions are met may the corresponding repairs move from implementation candidates to verified closure/promotion.