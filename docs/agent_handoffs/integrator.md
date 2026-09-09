# pATHENA Feature Integrator Handoff

## Current source of truth

- Develop baseline before this integration: `ee7894b4644dd2ec7db4778f2d9650d59b312c50`.
- Worker heads reviewed: errors `72b6c7bf0ed148ce1f2f274ae6940a14053c6655`; spec-core `850b631007ba3f359b9b16c619c692d853d75663`; backend `5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f`; UI `24d703dd1711ad663779784f96119dade62fe732`.
- No exact-current Develop canonical Quality was queued or in progress before mutation.
- UI exact-head Quality `34330894596` is in progress and therefore not READY. Its predecessor exact-head run `34325659408` failed.
- Backend has a new storage-test repair commit but no completed exact-green current-head Quality evidence yet; it remains non-READY conservatively.
- Spec/Core provides no new current product delta.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Progress this run — exact-Develop Quality trigger

No Worker slice was promotion-qualified. Exactly one collision-free cross-cutting CI slice was implemented: canonical `ATHENA Quality Gate` now runs on direct pushes to `develop/pathena-next` in addition to the existing `main` push and pull-request triggers.

This closes the evidence gap where Integrator product/test commits on Develop could exist without an exact-current canonical Quality run. `CANDIDATE_SHA`, concurrency with `cancel-in-progress: false`, all quality/storage/local-install/Windows jobs, the pypdf packaging smoke, and every test command remain unchanged.

No product, Storage, Recovery, Security, migration, Qt/UI, model/chat, process-topology, frozen-argv, or packaging behavior was modified. No test was skipped, xfailed, deleted, weakened, or bypassed.

## Quality / promotion state

- This integration intentionally causes its own exact-SHA canonical Quality on `develop/pathena-next` once the branch ref advances.
- After that run starts, Develop is frozen until it completes; no docs-only follow-up may supersede it.
- Beta/release-ready remains false until exact-current Develop Quality and the known Windows/Packaging/Runtime regression matrix are green.

## Next integration order

1. Wait for and consume the exact-current Develop Quality for this commit before any further Develop mutation.
2. Consume UI only if `24d703dd1711ad663779784f96119dade62fe732` finishes exact-green without a superseding Worker commit and its bounded delta remains compatible.
3. Keep Backend schema/WAL/storage work conservative until its exact-current Ruff/full-pytest lineage is green.
4. Preserve pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; and duplicate-column/Core-startup/storage-bootstrap signatures as Beta/release acceptance guards.

## Rules retained

No `main` mutation or promotion; no force push/history rewrite/auto-merge; no Skip/XFail; no weaker assertions; no Security/Storage/Recovery/Windows/validator relaxation; no fabricated evidence.
