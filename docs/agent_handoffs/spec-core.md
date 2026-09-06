# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@ef759aa0d6980da5adc3512b90e08512b7735082`.
- Stable read-only branch: `main` (unchanged; no mutation performed).
- Worker branch: `postmerge/spec-core`.
- Pre-run worker head: `2e0a840d370c5aa076f660caabb78ba166253e39`.
- Active worker heads reviewed: Backend `33be60ac2c7a6ddda234c8166846e233e94c4053`; UI `c249c0ec1c3a3a19617bcb5c6f3c2d4899d4a0fd`; Errors `61a65244ecd31797f47b7af1a454c3188193e2d5`; Integrator target is current Develop.
- Required `errors.md`, `backend.md`, `ui.md`, and `integrator.md` handoffs were reviewed before mutation.
- `bnbgrs/ATHENA` and `main` remained strictly read-only. No force update, rebase, or history rewrite was used.

## Verified prior slice — Personal Memory Why-is-this-remembered

Exact synchronized Core source head `c3ec46becb13362ab7a692cf88bef7389cdc5e47` passed canonical ATHENA Quality `34035539478 = success`.

The verified bounded product remains:

- `src/athena/memory/explanation.py@b4a182e38c335b747682e38b37fa3d5a63997f32`;
- `tests/unit/test_personal_memory_explanation.py@3bcbb71c6568dc23c1059cced48b813a610e105d`.

Current Develop had advanced beyond the previous synchronization but lacked only these two verified files. They were overlaid byte-identically onto exact Develop and both histories were joined through NON-FORCE two-parent synchronization `4dbf2f583221298748d4e67225031e1b678084eb`, parents prior Core head `2e0a840d370c5aa076f660caabb78ba166253e39` plus exact Develop `ef759aa0d6980da5adc3512b90e08512b7735082`.

Normal-Hybrid Search remains `VERIFIED` on current Develop and was not reopened. Its one-time attachment, capability gating, exact `query/model_id/limit/entity_type` delegation, canonical DTO mapping, semantic-unavailable propagation and application wiring identity remain preserved.

## New bounded Core slice — Beta Personal Memory §27 Memory View

Status: `IMPLEMENTED_PENDING_VERIFY`.

Spec anchor: `docs/beta/06_Personal_Memory.md` §27 requires the Personal-Memory view to expose content, type, scope, origin/creation mode, sensitivity, last confirmation and revisions. Existing durable repository/service contracts already provide canonical current state and ordered revision history; no new storage identity is required.

Product `e45ff4b839e2228485205547e1fbfe05da646b00` adds `src/athena/memory/view.py`:

- transport-neutral read-only projection from a real `PersonalMemorySnapshot` plus real canonical revision history;
- current content, kind, scope, origin, sensitivity, confidence and last-confirmed timestamp are copied from the canonical current revision;
- revision summaries are content-free and preserve real revision ID/number/time/origin/confirmation metadata;
- mixed memory IDs, non-contiguous history and history not ending at the current revision fail closed;
- `PROTECTED` plaintext snapshots fail closed and must use the Protected Content path rather than leaking ordinary-view content or metadata;
- no persistence write, synthetic provenance, Archive/Protected Search expansion, or PALLAS fake data is introduced.

Focused acceptance `20e911100b0d762f817da6c5a4d71dc083d0fcb9` adds `tests/unit/test_personal_memory_view.py` with a real SQLite create+revise path proving canonical current state/revision-history projection, plus a fail-closed Protected plaintext boundary regression.

Local checkout/test execution was attempted but remains blocked by transient DNS resolution of `github.com`; this is not treated as a product blocker. Canonical ATHENA Quality `34038684998` exists on exact product/test head `20e911100b0d762f817da6c5a4d71dc083d0fcb9` and is currently pending. No PASS or Integrator-ready claim is made for the new slice before exact completion.

## Collision avoidance

- Core owns only `src/athena/memory/view.py`, `tests/unit/test_personal_memory_view.py`, the verified explanation pair, and this handoff in this run.
- Backend owns current WAL/migration frame-count hardening; no storage/system file was changed by Core.
- UI owns Qt/presentation focus work; no styling or UI file was changed by Core.
- Errors reports no current OPEN Core defect requiring scope interruption.
- Review Queue/idempotency remains blocked unless a real durable proposal/review-decision identity is supplied; Core will not synthesize one or create deep storage schema work to simulate it.

## Integrator handoff

READY source evidence: Why-is-this-remembered exact head `c3ec46becb13362ab7a692cf88bef7389cdc5e47`, canonical Quality `34035539478 = success`, synchronized to exact current Develop through `4dbf2f583221298748d4e67225031e1b678084eb`.

NOT READY: Beta §27 Personal Memory View product `e45ff4b839e2228485205547e1fbfe05da646b00` + focused acceptance `20e911100b0d762f817da6c5a4d71dc083d0fcb9` until canonical Quality `34038684998` succeeds on that exact head or an exact-content descendant.

## Persistent release regression knowledge

Retain explicit Beta/release acceptance for Windows `pypdf` metadata and fail-closed frozen argv/two-EXE routing; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; the lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]` cluster; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; and `Failed to start service 'storage-bootstrap'`. Reopen only on exact-current reproduction, but do not declare Beta/release readiness while any known reproducible crash remains.

## Next Core step

Consume canonical Quality `34038684998`. If green, promote Beta §27 Personal Memory View to READY and hand its exact product/test SHA to Integrator, then take the highest disjoint evidence-backed CHAT/KNOWLEDGE/RESEARCH/PALLAS/Human-Control P0/P1/P2 gap. Personal-Memory Review Queue/idempotency remains excluded until a real durable proposal/review-decision identity exists. If the run fails, fix the exact Core-owned root cause without weakening Protected-content, provenance, persistence, Search, recovery, or Human-Control invariants.
