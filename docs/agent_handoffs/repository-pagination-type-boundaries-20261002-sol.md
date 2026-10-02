# Repository pagination runtime boundaries — 2026-10-02

BASE: develop/pathena-next@3357bf1e66d9d60d7b1c9e2d528c36632d89fbc5
BRANCH: fix/repository-pagination-type-boundaries-20261002-sol

## Root cause

The current repository layer contains several SQLite LIMIT boundaries that trust Python type annotations at runtime. Because bool is an int subclass, True/False satisfy ordinary numeric range expressions. Floats/strings/None fail inconsistently instead of at the repository contract.

The same defect is already being closed independently for KnowledgeRepository (#418) and SourceRepository (#422). A current-tree scan found four additional disjoint repository paths with the same shape.

## Owned fixes

- PersonalMemoryRepository.list_current(): reject bool/non-int before SQLite; keep 1..500.
- ClaimRepository.list_current(): reject bool/non-int before SQLite; keep 1..500.
- SourceAnalysisRepository.list_analyses_for_source(): reject bool/non-int; keep 1..1000.
- SourceAnchorRepository.list_for_source(): reject bool/non-int; keep 1..5000.

## Collision discipline

Open-PR ownership was checked before branch creation. No current open PR was found owning these four files. ChatRepository and JobRepository have similar patterns but were deliberately left untouched because active/legacy parallel work still references those repositories.

## Tests

Focused regressions use a database seam that raises on connection access. Invalid type/range cases therefore prove the boundary fails before SQLite.

Exact-head GitHub Actions are authoritative. Keep draft until terminal green.
