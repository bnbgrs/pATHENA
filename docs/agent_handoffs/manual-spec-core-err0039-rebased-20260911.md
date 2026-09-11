# ERR-0039 current-Develop repair handoff — 2026-09-11

## Lineage

- Base: `develop/pathena-next@e008e0fbf595da64bea64eb557dddeb2cd78bed0`
- Branch: `manual/spec-core-err0039-rebased-20260911`
- Initial rebased candidate: `faf752ca7ba47025681202f1049ba82a2ee750a2`
- Exact Ruff-remediated candidate: `98196f25c8c7e0a590e87711f3e54e0308b7f13b`
- PR: #113

This branch supersedes historical ERR-0039 diagnostic PRs #107 and #111, whose lineages were no longer clean current-Develop descendants.

## Root cause

The identity-transition feature and its six semantic tests were valid, but Ruff 0.15.22 rejected the import block in `tests/unit/test_identity_transition.py` with `I001`.

Multiple visually plausible import layouts were tested. The decisive evidence came from Ruff itself: focused run `34652701744` executed the repaired diagnostic remediation step and uploaded artifact `10284865229`. `ruff --fix` reported `1 fixed, 0 remaining` and produced the exact diff.

The required import boundary is:

```python
from uuid import UUID

import pytest

from athena.knowledge.identity_transition import MergeTransition, SplitTransition

A = UUID(...)
```

The subtle point is that Ruff expects the third-party and first-party imports separated, but only one blank line between the final import and module constants in this file. No configuration suppression was added.

## Verification

Exact head `98196f25c8c7e0a590e87711f3e54e0308b7f13b`:

- focused Core run `34652909370 = SUCCESS`;
- exact changed-file Ruff = SUCCESS;
- focused pytest = 6 passed;
- final fail-closed focused enforcement = SUCCESS;
- remediation step skipped because Ruff was already green.

The same exact product/test blobs were subsequently ported into the current all-known-errors consolidation PR #112 at commit `4d025b108cc7bd39e25c280bcc6b0d2e077b4dbb`.

## Bot rules

1. Use PR #113 or the exact equivalent blobs in PR #112 as ERR-0039 evidence; do not use #107/#111 for promotion.
2. Do not add `noqa`, disable `I001`, relax Ruff selection, delete tests, skip tests or change semantic assertions.
3. The six identity-transition tests are part of the repair contract and must remain green.
4. Do not independently duplicate this repair onto `postmerge/spec-core` while the consolidation candidate is qualifying.
5. Ledger status stays OPEN until exact combined promotion evidence meets the Error Ledger FIXED definition; focused green establishes the bounded repair, not Develop integration.
6. If #112 integrates equivalent blobs, #113 becomes provenance and must not be merged again.
