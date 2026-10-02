# Source repository list-boundary handoff — 2026-10-02

BASE: develop/pathena-next@3357bf1e66d9d60d7b1c9e2d528c36632d89fbc5
BRANCH: fix/source-repository-list-boundaries-20261002-sol

## Root cause

Python bool is a subclass of int. SourceRepository.list() and list_protected_in_scopes() only performed numeric range comparisons. True/False therefore crossed the public repository boundary as SQLite LIMIT values, while other non-integer values failed inconsistently through Python/SQLite rather than at the repository contract.

The protected-list path also returned early for an empty scope set before validating the caller-supplied limit.

## Fix

- reject bool and every non-int limit with TypeError before SQLite;
- preserve existing integer ranges (1..500 and 1..10001);
- validate the protected-list limit before the empty-scope fast path;
- add focused regressions using a database seam that raises on any invalid-path access.

## Collision check

No open PR was found declaring ownership of src/athena/source/repository.py at branch creation. This slice is disjoint from PR #420, which owns Source byte capture/service/model/representation files but not SourceRepository.

## Validation

Exact-head CI is required. Do not claim PASS from static inspection.
