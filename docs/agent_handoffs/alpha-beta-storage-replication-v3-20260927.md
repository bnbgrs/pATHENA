# Alpha/Beta Storage replication v3 — durable state

Date: 2026-09-27
Base Develop: `cd891f602a1de48f90e9c0cb0f83cbff15ba1e62`
Branch: `fix/alpha-beta-storage-replication-v3`

## This slice

- advances the SQLite contract to schema v41;
- adds restart-safe `replication_targets` and `replication_commits` state;
- persists a monotone confirmed commit sequence and verified head hash per
  `long_term_root` target;
- fences staging against sequence gaps and unexpected previous heads;
- confirms exactly one pending commit at a time in the same transaction as the
  target watermark update;
- persists explicit conflict and recovery states;
- fails closed when partially present replication tables have an incompatible
  column contract;
- keeps replication state payload-free: no plaintext or Protected Content is
  stored in these tables.

## Qualification

- structured-replication repository and migration regressions;
- schema evolution and verification boundary tests;
- all affected historical schema/backup/protected-content regressions;
- Ruff on every changed Python file;
- mypy on all changed storage production modules;
- `git diff --check`.

## Deliberately not included

The next independent slice must add the canonical commit-bundle serializer and
verified `long_term_root` filesystem publication. It must then compare the
target head before publication, enter conflict/recovery on unexpected history,
and never overwrite target history silently. Durable worker composition and
snapshot/replay follow only after that verified write boundary exists.
