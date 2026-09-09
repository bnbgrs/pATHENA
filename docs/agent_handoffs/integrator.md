# pATHENA Feature Integrator Handoff

## Current source of truth

- Develop baseline before this integration: `0abc53a35e6c99bf7070875633d3f81f6bc09395`.
- Exact Develop canonical Quality `34331712073@0abc53a35e6c99bf7070875633d3f81f6bc09395 = SUCCESS`; no exact-current queued/in-progress Develop run existed immediately before mutation.
- Worker heads reviewed: errors `72b6c7bf0ed148ce1f2f274ae6940a14053c6655`; spec-core `850b631007ba3f359b9b16c619c692d853d75663`; backend `8dd0f50db0d593808093a8a0538097cc2e5c2d24`; UI `04a4e5d29421dc786c4894fd2091726fdeb5813a`.
- UI exact-head Quality `34336304734` is `IN_PROGRESS`, so UI is not READY. The preceding UI candidate `24d703dd1711ad663779784f96119dade62fe732` failed exact-head Quality `34330894596`.
- Backend exact-head canonical Quality is failed; schema/WAL/v41 work remains non-READY conservatively.
- Spec/Core differs from current Develop only in its handoff document; no new product delta is available for integration.
- Error evidence keeps Backend v41/schema/WAL root causes in progress; no historical release signature is reopened without current exact reproduction.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` and `bnbgrs/ATHENA` remain read-only and untouched.

## Progress this run — canonical Quality policy regression guard

No Worker slice was promotion-qualified. Exactly one collision-free cross-cutting test slice was implemented: `tests/unit/test_quality_workflow_contract.py` now locks the canonical CI policy that direct pushes to `develop/pathena-next` run Quality without cancellation and that the Local install smoke retains the fail-closed `athena-packaging-smoke --json` pypdf metadata check.

This is a regression guard only. It does not alter workflow execution, product behavior, test selection, Storage, Recovery, Security, migration, Qt/UI, model/chat behavior, process topology, frozen argv, packaging, or Windows semantics. No Skip/XFail or assertion weakening is introduced.

## Current UI / visual state

- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` on Develop still records all eleven real product surfaces as implemented pending visual review; no screenshot-level MATCH is claimed.
- `docs/ui/VISUAL_GAP_LEDGER.md` on Develop retains only evidence-backed gaps and the `VISUAL_REFERENCE_PENDING` blocker for pixel/composition claims.
- Current UI worker changes remain held until exact-head Quality completes successfully without superseding commits.

## Quality / promotion state

- Advancing Develop with this commit must trigger a new exact-SHA canonical Quality run.
- Once that run is queued/in-progress, Develop is frozen until completion; no docs-only follow-up may supersede it.
- Beta/release-ready remains false until exact-current Develop Quality and the known Windows/Packaging/Runtime regression matrix are green.

## Next integration order

1. Consume the exact-current Develop Quality for this commit before any further Develop mutation.
2. Consume UI only if the current exact worker head finishes green without a superseding commit and its bounded delta remains compatible.
3. Keep Backend schema/WAL/storage work conservative until its exact-current Ruff/full-pytest lineage is green.
4. Preserve pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; and duplicate-column/Core-startup/storage-bootstrap signatures as Beta/release acceptance guards.

## Rules retained

No `main` mutation or promotion; no force push/history rewrite/auto-merge; no Skip/XFail; no weaker assertions; no Security/Storage/Recovery/Windows/validator relaxation; no fabricated evidence or percentages.
