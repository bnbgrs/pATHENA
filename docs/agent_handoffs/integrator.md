# pATHENA Feature Integrator Handoff

## Authoritative integration baseline

- Integration target: `develop/pathena-next`.
- Current product version: `0.1.0`.
- This handoff intentionally does **not** freeze a Develop SHA or a static `PROMOTION_READY` flag. Those values become stale as soon as a new commit lands.
- The authoritative branch SHA must be read directly from GitHub before every integration.
- `main` remains outside the automatic integration path.

## Source-of-truth order

Use these sources in this order:

1. the exact current `develop/pathena-next` tree and its exact-head CI;
2. open GitHub issues and pull requests;
3. `docs/development/ALPHA_BETA_PROGRESS.md`;
4. `docs/agent_handoffs/errors.md` and `docs/agent_logs/ERROR_LEDGER.md`;
5. exact-SHA Quality, Windows Package, Visual and Promotion Readiness workflow evidence.

`docs/agent_coordination/feature_gap_backlog.md` is a historical 2026-08-24 snapshot, not an active integration queue. Old `postmerge/*` and worker branches are not merge candidates merely because they contain commits; they must be re-diffed against current Develop and independently requalified before any bounded slice can be considered.

## Current closure state

- The v0.1.0 release lineage passed canonical Quality and the native Windows Package gate on exact Develop SHA `30243bb2dad38e1c7cb7a3dff664a86bf838960a` before this documentation consolidation.
- Current Error handoff/ledger state is closed: `OPEN: none`, `IN_PROGRESS: none`, `FIXED_PENDING_VERIFY: none`.
- The stale Settings `IMPLEMENTED_PENDING_VERIFY` rows have been reconciled against current product behavior and exact-head Quality evidence.
- The historical eleven-reference review is complete: 11/11 originals and 11/11 native captures were inspected. The result is intentionally `MATCH=0/11`; the current visual baseline is a regression lock, not a claim of pixel parity.
- New work is opened only from a reproduced current defect, an explicit current requirement gap, or a new user-directed change.

## Integration rules

- Inspect current Develop before selecting work.
- Never merge a stale worker branch wholesale.
- Prefer one bounded, independently reviewed slice.
- Preserve Security, Storage, Recovery, Windows process, packaging and provenance guards.
- Do not add Skip/XFail or weaken assertions to make a gate green.
- Use focused tests during implementation, then exact-head canonical gates before integration.
- Do not fabricate success, provenance, UI state or release readiness.

## Promotion readiness

Promotion readiness is **workflow-derived, not document-derived**. The authoritative decision is the `pATHENA promotion readiness` workflow on the exact `bot/pathena-candidate` SHA. A package manifest may claim only its own package smoke; full `release_ready` status is emitted only by the exact-SHA promotion certification after Quality, Windows Package, promotion guard and Windows release contracts are all green.
