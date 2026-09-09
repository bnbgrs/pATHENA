# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Shared baseline reviewed: `develop/pathena-next@24364b858e15fd9e3b06a9ee2eaf1f580b51364c`.
- Worker at run start: `postmerge/spec-core@0c9189954047306cfea947209b51e1a4d0a50aa3`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- Current Errors/Backend/UI/Integrator handoffs and the current Research implementation/acceptance path were re-read before mutation.

## Bounded Core slice: restore Delta freeze support on current Develop

The Delta Research product/test slice is already integrated on Develop, but exact-current canonical Quality `34379757715` failed twice in the full pytest step. Attempt 2 diagnostics show exactly one failure: `tests/unit/test_research_delta.py::test_delta_research_freezes_only_new_explicit_sources`, raising `ResearchScopeUnsupportedError: Foundation discovery does not support Research mode 'delta'`; summary: `1 failed, 4821 passed, 3 skipped, 2 warnings`.

The root cause is precise: current Develop's `ResearchRepository.freeze_local_candidates()` allowlist contains `LOCAL_EXHAUSTIVE`, `HISTORICAL_BACKFILL`, and `LOCAL_PLUS_WEB`, but omitted `ResearchMode.DELTA`. The exact prior worker blob already contains only the required additive `ResearchMode.DELTA` entry at this boundary and previously passed canonical Quality `34370631502` on exact worker SHA `0c9189954047306cfea947209b51e1a4d0a50aa3`.

This candidate therefore restores that one fail-closed product line onto the current Develop tree. Existing explicit-source selection, pinned snapshot semantics, missing-source rejection, durable payload validation, storage, transport, recovery, security, UI, and release guards are unchanged. No fake Sources, Claims, Evidence, Knowledge, Provenance, or PALLAS state is introduced.

## Verification discipline

- Existing focused acceptance remains authoritative: Delta freezes only explicitly selected later Sources into a separate scope and rejects an empty explicit Source set before persistence.
- Exact-current Develop canonical failure was consumed before mutation; all non-pytest lanes were green.
- Candidate requires its own exact-SHA canonical Quality before Integrator-ready status.
- Once canonical Quality starts on this candidate, no further `postmerge/spec-core` commit is permitted until that result is consumed.

## Readiness

`CANDIDATE_PENDING_EXACT_SHA`: bounded current-Develop repair for Delta candidate freezing. Integrator-ready only after exact-SHA canonical success and compatible Develop baseline.
