# Quality Gate: knowledge workspace proposal typing

Date: 2026-08-23

## Failing gate

GitHub Actions run `32621416247`, job `97150021451`, on pATHENA branch `agent/pathena` failed in `mypy` after the specification validator and Ruff both passed.

Reported errors:

```text
src/athena/desktop/knowledge_workspace.py:141: error: Incompatible types in assignment
(expression has type "ClaimProposalResponse", variable has type "KnowledgeUnitProposalResponse") [assignment]
src/athena/desktop/knowledge_workspace.py:143: error: "KnowledgeUnitProposalResponse" has no attribute "claim_kind" [attr-defined]
src/athena/desktop/knowledge_workspace.py:145: error: "KnowledgeUnitProposalResponse" has no attribute "statement" [attr-defined]
Found 3 errors in 1 file (checked 237 source files)
```

## Root cause

`KnowledgeWorkspace.apply_extraction()` reused the local loop variable name `proposal` for two different statically typed collections:

- `payload.knowledge_units` contains `KnowledgeUnitProposalResponse` values.
- `payload.claims` contains `ClaimProposalResponse` values.

mypy keeps the inferred type of a local variable in the scope and therefore rejected assigning a `ClaimProposalResponse` to the already inferred `KnowledgeUnitProposalResponse` variable. The missing-attribute errors were consequences of the same type collision, not separate defects.

## Fix

The two loops now use distinct variable names:

- `knowledge_proposal`
- `claim_proposal`

No behavior, API contract, persistence logic, or feature semantics were changed.

Fix commit: `c8cfd31d59cdd1cffbecdf692b54305c52f866dc`

## Verification target

The next full CI quality run must confirm:

1. specification validator remains green;
2. Ruff remains green;
3. mypy passes this file and proceeds beyond the previous blocker;
4. any next failure is treated independently and documented before modification.
