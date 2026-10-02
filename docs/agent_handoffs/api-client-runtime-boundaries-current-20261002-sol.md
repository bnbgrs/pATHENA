# pATHENA handoff — Core API client runtime boundaries — 2026-10-02

BASE: develop/pathena-next@3357bf1e66d9d60d7b1c9e2d528c36632d89fbc5
BRANCH: api/client-runtime-boundaries-current-20261002-sol
LEGACY_SOURCE: PR #378 @ bf7faeaf4f40020c0744011b1c2d2a6b449433a9

## Why this reconstruction exists

The old #378 hardened the local desktop Core client, but its full pytest job failed during test collection because the regression suite used 10**10000 as a parametrized value. Python 3.12 refused the resulting >4300-digit decimal conversion while pytest built the parameter ID. The product code itself had already passed specification validation, Ruff, mypy, Windows path safety, Linux storage regressions and local-install smoke.

Current Develop has newer Universal Search work in src/athena/api/client.py, so the old file was not copied. Only the missing runtime-boundary hunks were replayed into today's client, preserving the newer search contract. The overflow regression now uses 10**400, which still raises OverflowError when converted to float but stays below Python's decimal-string safety limit.

## Product contract

- transport and generation timeouts must be positive finite numbers and reject bool/non-numeric values;
- chat pagination rejects bool/non-int values before discovery/network access;
- numeric response fields reject NaN, Infinity and int->float overflow as invalid_response;
- runtime bootstrap rejects link/reparse boundaries anywhere in its ancestor path;
- discovery/token leaf checks use the shared is_link_boundary trust predicate.

## Files

- src/athena/api/client.py
- tests/unit/test_core_api_client.py
- docs/agent_handoffs/api-client-runtime-boundaries-current-20261002-sol.md

## Validation truth

Do not claim this reconstructed head green until exact-head GitHub Actions are terminal. Legacy #378 evidence is supporting evidence only.

## Next actions

1. Run canonical Quality on the exact reconstructed head.
2. Fix only branch-owned failures.
3. Merge only after terminal green evidence and drift re-check.
