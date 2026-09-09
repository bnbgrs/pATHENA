# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Shared baseline reviewed this run: `develop/pathena-next@5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba`.
- Worker before this candidate: `postmerge/spec-core@6b833fdbe9066dbd17f8a54272b0543d7c5d5ece`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- Current Errors/Backend/UI/Integrator handoffs, Alpha/Beta Research spec, Research models/service, capability/test coverage and release guards were re-read before mutation.

## Bounded Core slice: explicit-source Delta Research

Beta Exhaustive Research states that data arriving after a frozen snapshot is not silently absorbed and that new relevant data may create a Delta Research job. The current domain model already contains `ResearchMode.DELTA`, while the current Research service exposes Local Exhaustive, Local+Web, Scoped Project and Historical Backfill enqueue composition but no Delta enqueue path.

This candidate adds `athena.research.delta.enqueue_delta()` as a bounded Core composition layer. It requires at least one real canonical Source UUID, creates a fresh `research.exhaustive` job in `ResearchMode.DELTA`, and restricts the scope to those explicit Source identities. It intentionally does not add a Storage migration or invent parent-Research provenance not represented by the current schema.

Acceptance coverage in `tests/unit/test_research_delta.py` proves that a Source captured after an original Research snapshot can be frozen into a new Delta scope without silently absorbing the original Source, and that an empty Source set fails before job persistence.

## Test / CI evidence

- Focused local execution was attempted first, but the runner could not resolve `github.com`; no local PASS is claimed.
- The candidate includes the focused acceptance tests above and is not Integrator-ready until exact-SHA canonical Quality completes successfully. If Quality is queued/in progress, no further worker commit is permitted.

## Closed / retained contracts

- Adaptive DirectChat 2048-context/output-reserve behavior remains closed absent new exact-current regression evidence.
- Normal/Hybrid Search Core API composition remains closed absent new exact-current regression evidence.
- Contradiction-review enqueue remains unchanged without a concrete current production bypass.
- No fake Sources, Claims, Knowledge, Evidence, Provenance or PALLAS state is introduced.

## Ownership boundaries / persistent guards

- No Backend/Storage schema, WAL, transport, recovery, security or UI styling work is duplicated.
- pypdf/Frozen argv/two-EXE, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock/path-safety and duplicate-column/Core-startup/storage-bootstrap guards remain unchanged and binding.
- No force push, history rewrite, Skip/XFail or guard weakening.

## Readiness

`CANDIDATE_PENDING_EXACT_SHA`: bounded product + acceptance-test diff is based on current Develop and preserves prior worker history. Integrator-ready requires exact-SHA Quality success and a still-compatible Develop baseline.
