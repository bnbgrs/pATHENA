# Spec/Core Handoff

## Current baseline

- Develop baseline checked: `develop/pathena-next@cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`.
- Pre-run Core worker: `postmerge/spec-core@e0e04088f95799a6aa94dde3f67e7aa1fc852a8b`.
- History-preserving NON-FORCE synchronization: `ce75b255ab99e3db4a36a51bd820513037764b78`, parents prior Core head `e0e04088f95799a6aa94dde3f67e7aa1fc852a8b` and exact Develop `cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`.
- The synchronized tree uses current Develop as authoritative for product/tests/integrator state and preserves this Core-owned handoff.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched. No force update, rebase or history rewrite occurred.

## Required handoffs / active heads checked

- Error handoff is current on Develop `cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`; `ERR-0026` through `ERR-0029` remain Backend-owned/in progress.
- Backend active head: `postmerge/backend@0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d`; canonical Quality `34269071606` completed FAILURE. Windows path safety, Local install smoke, Linux storage regressions, specification validator and mypy passed; Ruff and full pytest failed. Backend v41 / §75 persistence remains non-consumable.
- Backend handoff itself is older than the active Backend head; Error handoff contains the newer exact failure evidence and requires exact Ruff/assertion diagnostics before another Backend mutation.
- Integrator handoff on current Develop was checked through the baseline sync; current Develop-only deltas were Integrator/UI startup-accessibility changes and are authoritative.

## Preserved Core contracts

Normal Hybrid Search remains inherited and unchanged: one-time `attach_normal_search`; `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; `SemanticRetrievalUnavailableError` propagates unchanged; `app.api._normal_search is app.hybrid_retrieval`.

Research §68–§74 and verified §65 partial-result semantics remain preserved. No synthetic provenance, Archive/Protected expansion, fake PALLAS data, Skip/XFail, assertion weakening, force push, main mutation or ATHENA mutation.

## §75 Delta Research — blocked on exact-green Backend persistence

The bounded Core contract remains unchanged: explicit completed `base_scope_id`, durable lower commit boundary, pinned upper `snapshot_commit_seq`, candidate freeze only in `(lower_commit_seq, snapshot_commit_seq]`, and restart-stable boundary/CandidateSet identity without wall-clock substitution.

Core must not consume Backend v41 while exact Backend Quality is red. Current Backend/Error evidence owns schema/migration/WAL recovery under `ERR-0026` through `ERR-0029`.

## Independent-gap scan

The current Develop Alpha/Beta tracker remains evidence-backed: Normal Hybrid Search, contradiction composition, Exhaustive Research acceptance through §74, and §65 Partial Result are VERIFIED. The current READY Scout gaps remain Backend/Backend-primary where they require durable job/source schema, scheduler, transport or provider work. A current top-level source-tree scan also found no separate PALLAS Core module to mutate safely without first deriving a normative composition contract from the relevant spec/code path; no decorative/fake-data implementation is permitted.

This run therefore made concrete non-repetitive progress by synchronizing the materially diverged Core branch from 181 commits behind / 2 ahead to the exact current Develop product tree while preserving Core handoff history, and by refreshing the exact Backend failure point to Quality `34269071606@0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d` rather than reusing stale evidence.

## Required next actions

1. Consume the first exact-green Backend successor that closes the v41 prerequisite.
2. Once verified persistence is available on the shared baseline, execute §75 immediately: `enqueue_delta`, one-time durable boundary binding, candidate selection over `(lower_commit_seq, snapshot_commit_seq]`, restart/resume identity acceptance, focused tests then canonical Quality.
3. If Backend remains red, inspect newly versioned Alpha/Beta/Capability evidence for a genuinely independent Core-owned P0/P1/P2 gap and implement it; do not repeat §65/§75 analysis or duplicate Backend work.
4. Preserve release regression matrix: pypdf/frozen argv/two-EXE routing, bounded worker tree, adaptive 2048-context reserve, lane-lock ownership cluster, duplicate-column startup, Core startup and storage-bootstrap signatures. Historical signatures become OPEN only on exact-SHA reproduction.
