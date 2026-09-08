# Spec/Core Handoff

## Current baseline

- Develop baseline checked: `develop/pathena-next@9606fdf8f43e97136288b41be922f97477ffc102`.
- Pre-run Core worker: `postmerge/spec-core@d8ee2c867b2670455d88433fd213f4217ac2389a`.
- History-preserving NON-FORCE synchronization: `bfc01dc724ea55adfd4f446b82d41deb1a3af8ea`, parents prior Core head `d8ee2c867b2670455d88433fd213f4217ac2389a` and exact Develop `9606fdf8f43e97136288b41be922f97477ffc102`.
- The synchronized tree uses current Develop as authoritative for product/tests/integrator state and preserves this Core-owned handoff.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched. No force update, rebase or history rewrite occurred.

## Required handoffs / active heads checked

- Errors handoff is based on Develop `9606fdf8f43e97136288b41be922f97477ffc102`; `ERR-0026` through `ERR-0029` remain Backend-owned/in progress.
- Backend active head: `postmerge/backend@d2cc107a38b0ae56bd70191b9ac2149c19b2fb26`; canonical Quality `34263109322` is exact FAILURE with Ruff and full pytest red while Windows path safety, Local install, Linux storage, specification validator and mypy pass. Backend v41 / §75 persistence is not consumable.
- UI active head: `postmerge/ui@19924adc2881b3eff06a6c4c343abba7e635ecbc`; UI work is disjoint and presentation/accessibility-owned.
- Integrator handoff checked on exact Develop; §65 is integrated and §75 remains held on Backend.

## Preserved Core contracts

Normal Hybrid Search remains inherited and unchanged: one-time `attach_normal_search`; `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; `SemanticRetrievalUnavailableError` propagates unchanged; `app.api._normal_search is app.hybrid_retrieval`.

Research §68–§74 and verified §65 partial-result semantics remain preserved. No synthetic provenance, Archive/Protected expansion, fake PALLAS data, Skip/XFail, assertion weakening, force push, main mutation or ATHENA mutation.

## §75 Delta Research — blocked on exact-green Backend persistence

The bounded Core contract remains unchanged: explicit completed `base_scope_id`, durable lower commit boundary, pinned upper `snapshot_commit_seq`, candidate freeze only in `(lower_commit_seq, snapshot_commit_seq]`, and restart-stable boundary/CandidateSet identity without wall-clock substitution.

Core must not consume Backend v41 while exact Backend Quality is red. Current Backend/Error evidence owns schema/migration/WAL recovery under `ERR-0026` through `ERR-0029`.

## Independent-gap scan

The current Develop Alpha/Beta tracker remains evidence-backed: Normal Hybrid Search, contradiction composition, Exhaustive Research acceptance through §74, and §65 Partial Result are VERIFIED. The currently READY Scout gaps exposed in the shared backlog remain Backend/Backend-primary because they require durable job/source schema, scheduler, transport, or provider work. No separate documented Core-owned P0/P1/P2 gap is currently READY without crossing ownership boundaries.

## Required next actions

1. Consume the first exact-green Backend successor that closes the v41 prerequisite.
2. Once that verified persistence is available on the shared baseline, execute §75 immediately: `enqueue_delta`, one-time durable boundary binding, candidate selection over `(lower_commit_seq, snapshot_commit_seq]`, restart/resume identity acceptance, focused tests then canonical Quality.
3. If Backend remains red, inspect newly versioned Alpha/Beta/Capability evidence for a genuinely independent Core-owned P0/P1/P2 gap; do not repeat §65/§75 analysis or duplicate Backend work.
4. Preserve release regression matrix: pypdf/frozen argv/two-EXE routing, bounded worker tree, adaptive 2048-context reserve, lane-lock ownership cluster, duplicate-column startup, Core startup and storage-bootstrap signatures. Historical signatures become OPEN only on exact-SHA reproduction.
