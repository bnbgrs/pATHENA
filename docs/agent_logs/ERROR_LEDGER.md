# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

- Stable IDs use `ERR-####`.
- Only failures reproduced or evidenced on the stated SHA are opened.
- Historical failures are not carried forward unless their signature recurs on the current baseline.
- Cascades are deduplicated under their primary root cause.
- `FIXED` requires observed verification; unverified fixes remain `FIXED_PENDING_VERIFY`.
- Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`.

## Current baseline

- Baseline branch: `develop/pathena-next`
- Baseline SHA: `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Error worker synchronized history-preservingly and NON-FORCE with current Develop via merge commit `7d74347e3204ebe459e2fe6bf93cbd631633051f`.

## Current error state

- OPEN: none assigned to error-worker product mutation.
- IN_PROGRESS: none.
- BLOCKED: `ERR-0001` and `ERR-0002` are Backend-owned; error worker must not patch either root cause in parallel.

## Current scan

- Exact current Develop `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5` contains coordination/tracker changes only; ERR-0001 product guards are still unintegrated.
- Backend worker `fab69755fd0a77dea9bfd2b6effc4d9ceb943305` contains ERR-0001 product fix `780d25d74ce2e310b6a4bc434f547a23163e8b78`.
- Canonical Quality run `33744816398` on exact Backend head reports `Quality — Ruff` = FAILURE while specification validator, mypy, Windows path safety, Linux storage regressions and local install smoke are successful; pytest was still running when inspected.
- The ERR-0001 patch introduces `type(...) is not ...` runtime guards in `src/athena/lifecycle/deletion.py`; this is the leading root-cause hypothesis for Ruff E721, but the exact Ruff diagnostic text has not yet been retrieved, so ERR-0002 remains a verified Ruff failure with a bounded hypothesis rather than a claimed exact rule code.

## Entries

### ERR-0001 — Deletion-ledger mutation/cursor boundaries accept malformed runtime types

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5`
- severity: P2
- area: Storage / Persistence / Deletion Ledger / Recovery boundary
- status: `BLOCKED`
- exact evidence:
  - Current Develop still does not contain the Backend product guard fix.
  - Backend commit `780d25d74ce2e310b6a4bc434f547a23163e8b78` adds fail-before-SQL runtime type/range guards.
  - Backend exact-head Quality run `33744816398` is not green because its Ruff step failed; therefore the repair is not integration-ready.
- reproducible path:
  1. On current Develop, malformed `entity_type` reaches `.strip()` before intended boundary validation.
  2. Bool values can cross integer timestamp/commit-sequence/cursor boundaries.
- primary root cause: durable deletion-ledger APIs rely on annotations/relational comparisons instead of explicit bool-safe runtime validation before SQL access.
- affected files: `src/athena/lifecycle/deletion.py`; `tests/unit/test_deletion_ledger_boundaries.py`; existing deletion-ledger/lifecycle recovery regressions.
- fix_commit: Backend candidate `780d25d74ce2e310b6a4bc434f547a23163e8b78`, not integrated.
- verification executed: current Develop/Backend branch heads reviewed; Backend patch reviewed; Quality run/job state inspected.
- remaining risks: candidate repair is currently blocked by a lint regression; no `FIXED` claim until integrated and independently verified on exact Develop.
- integrator handoff: do not integrate Backend candidate until ERR-0002 is corrected without weakening exact runtime validation and focused/regression Quality is green.
- blocked reason: active ownership collision avoidance with `postmerge/backend`.

### ERR-0002 — Backend deletion-boundary candidate fails canonical Ruff

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `fab69755fd0a77dea9bfd2b6effc4d9ceb943305`
- severity: P2
- area: Quality / Python lint / Storage boundary candidate
- status: `BLOCKED`
- exact evidence:
  - Canonical Quality run `33744816398`, job `Python 3.12 quality`, step `Quality — Ruff` completed with `failure` on exact Backend head `fab69755fd0a77dea9bfd2b6effc4d9ceb943305`.
  - In the same run, specification validator and mypy succeeded; Windows path safety, Linux storage regressions and local install smoke also succeeded.
  - Product commit `780d25d74ce2e310b6a4bc434f547a23163e8b78` changes only `src/athena/lifecycle/deletion.py` and introduces three `type(...) is not ...` checks.
- reproducible path: run the repository canonical Ruff check against Backend head `fab69755fd0a77dea9bfd2b6effc4d9ceb943305`; canonical CI already reproduces failure. Exact local command/rule text remains pending diagnostics.
- primary root cause or hypothesis: likely Ruff E721 triggered by direct `type(...) is not str/int` comparisons introduced in the ERR-0001 candidate; exact rule text must be confirmed from diagnostics before marking root cause confirmed.
- affected files: `src/athena/lifecycle/deletion.py`; potentially only the three newly introduced exact-type guards.
- fix_commit: none.
- verification executed: canonical workflow/job API inspected; candidate commit diff independently reviewed.
- remaining risks: replacing direct type checks must preserve the intended bool rejection and fail-before-SQL semantics; using plain `isinstance(x, int)` would regress bool safety.
- integrator handoff: Backend should retrieve/confirm the Ruff diagnostic, replace the lint-invalid exact-type formulation with a Ruff-clean bool-safe equivalent, rerun focused deletion-boundary tests plus canonical Quality, and hand off only one exact verified head.
- blocked reason: active ownership belongs to `postmerge/backend`; Error worker does not parallel-edit the candidate product file.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
