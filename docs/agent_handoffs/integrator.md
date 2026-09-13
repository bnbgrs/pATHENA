# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `09d43c348420dc5ad0eb2be80ebf8681ae8f25c5`.
- Exact parent canonical Quality `34753048193 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration 1 — truthful source-age stale signal

Bounded source candidate: `60b82913ed64f13a92c52bb52448011ac208dacf`.
Exact evidence: Core Focused `34749319038 = SUCCESS`; canonical Quality `34749319064 = SUCCESS`.
Only `src/athena/knowledge/staleness_policy.py` and `tests/unit/test_stale_knowledge_policy.py` are extracted. The existing staleness policy now accepts only explicit caller-supplied source observation time plus maximum age, preserves simultaneous validity/source-age reasons deterministically, treats exact boundaries as not stale, and fails closed on partial, malformed, negative or future temporal evidence. It does not synthesize source age, truth status, provenance, replacement revisions or jobs.

## Iteration 2 — explicit user-correction guard

Bounded source candidate: `367bf6ee879450373cde5f116ca78fbe28a2dbac`.
Exact evidence: Core Focused `34754120108 = SUCCESS`; canonical Quality `34754120154 = SUCCESS`.
Only `src/athena/knowledge/user_correction_policy.py` and `tests/unit/test_knowledge_user_correction_policy.py` are extracted. Explicit user corrections cannot be silently replaced by automation; absent, older or equal evidence preserves them; genuinely newer evidence opens human review; a later explicit user decision can revise them; malformed actors/timestamps fail closed. No source, evidence, provenance, truth status or revision is fabricated.

## Candidate intentionally blocked

The historical send-button tokenization is not safe as a one-file Develop integration. Current `develop/pathena-next` `ShellGeometry` does not define `composer_action_size`, while the UI candidate stylesheet references it. Therefore the stylesheet-only ERR-0053 extraction would introduce an invalid attribute dependency. UI must provide a bounded current-baseline slice that includes the compatible geometry token plus focused tests and exact-head evidence; no broad UI branch promotion is allowed.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` remains historical where newer exact-SHA evidence exists.
- Eleven-screen parity remains fail-closed: no visual `MATCH` without an opened original reference plus a real rendered state from the exact implementation SHA.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.
