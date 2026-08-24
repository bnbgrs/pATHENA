# pATHENA Coordination Conflicts

Single source of truth for real bot, specification and ownership conflicts on `agent/pathena`.

Conflict status values: `OPEN`, `RESOLVED`, `ESCALATED`, `STALE`.
Canonical Ownership values: `QUALITY`, `BACKEND`, `UI`, `SECURITY`, `FEATURE`, `MIXED`, `EXTERNAL`.

## CONFLICT-001 — Windows durable publication ownership overlap

- Type: Ownership / implementation-boundary conflict.
- Evidence: Quality `FGATE-008`/`QG-WINDOWS-DURABLE-WRITE-PARENT-IDENTITY`, Backend `BE-038`, and Security `SEC-012` describe the same Windows parent-identity gap from different ownership perspectives. Backend owns the shared durable-filesystem implementation; Security owns the adversarial security invariant; Quality owns integrative/native-Windows verification.
- Affected IDs/files: `FGATE-008`, `BE-038`, `SEC-012`, `src/athena/storage/durable_fs.py`, migration/API consumers and Windows race regressions.
- Side A: Security queue previously treated the residual Windows exposure as a Security-owned continuation because it affects bearer-token confidentiality and filesystem trust boundaries.
- Side B: Backend queue treats HANDLE-bound durable publication as Backend implementation work because the shared storage primitive is Backend-owned and serves non-security migration consumers too.
- Risk: duplicate incompatible implementations, Security changing storage internals, or Quality treating a security invariant as a mere test-harness issue.
- Proposed resolution: canonical `Ownership: MIXED`; Primary implementation owner `BACKEND`; Secondary reviewers `SECURITY`; Verification owner `QUALITY`. Stable sub-slices are `FGATE-008-BE`, `FGATE-008-SEC`, and `FGATE-008-QA`.
- Required owner/arbitrator: QUALITY arbitration; BACKEND implementation; SECURITY review.
- Status: RESOLVED.
- Last check: 2026-08-24 on candidate SHA `31b580609527f828b87854207bd1c33c3a4bfec6`.
- Full-Gate link: `FGATE-008` ↔ `CONFLICT-001`.

## CONFLICT-002 — Plain HTTP external-fetch product policy

- Type: Specification / Security-vs-Feature product-policy conflict.
- Evidence: `SEC-002` records that `ExternalFetchGateway` intentionally supports both `http://` and `https://`; authorization/SSRF/DNS controls do not answer whether plaintext HTTP is an intended product capability. Security can justify HTTPS-only default behavior, while Feature/Product can justify explicit HTTP for legacy/local research endpoints.
- Affected IDs/files: `SEC-002`, Feature external-fetch/Tor/internet policy, `src/athena/external/gateway.py`.
- Side A: SECURITY — plaintext HTTP permits transport confidentiality/integrity loss even when the destination is explicitly authorized.
- Side B: FEATURE — HTTP may be a deliberate compatibility capability; removing it is a product behavior change rather than a pure security repair.
- Risk: Security silently removes intended functionality, or Feature preserves plaintext transport without an explicit risk/UX contract.
- Proposed resolution: **USER DECISION REQUIRED**. Option A: HTTPS-only by default with explicit high-friction per-request/per-destination HTTP opt-in and provenance marking. Option B: retain current HTTP(S) parity after explicit approval. Recommended safe default: Option A.
- Required owner/arbitrator: USER for product policy; FEATURE implements chosen behavior; SECURITY reviews transport invariant; QUALITY verifies.
- Status: ESCALATED.
- Last check: 2026-08-24; current candidate SHA does not make this a required Full-Gate blocker.

## CONFLICT-003 — Startup database identity ownership overlap

- Type: Ownership / cross-layer security invariant.
- Evidence: `SEC-014` identifies preflight-to-live-writer database identity drift across `AthenaApplication.start()`, storage preflight, bootstrap and SQLite open. The invariant is security-sensitive, but the productive lifecycle and SQLite writer implementation are Backend-owned.
- Affected IDs/files: `SEC-014`, future Backend storage slice, `src/athena/core/application.py`, `src/athena/storage/recovery.py`, `src/athena/storage/bootstrap.py`, `src/athena/storage/database.py`.
- Side A: SECURITY — validated database/root identity must remain trustworthy through writable activation.
- Side B: BACKEND — only the storage/application lifecycle can implement an atomic or identity-bound handoff without duplicating writer logic.
- Risk: partial check-then-open mitigations, duplicate identity logic, or Security directly owning Backend lifecycle code.
- Proposed resolution: canonical `Ownership: MIXED`; Primary implementation owner `BACKEND`; Secondary reviewers `SECURITY`; Verification owner `QUALITY`. Sub-slices: `CONFLICT-003-BE` Owner BACKEND — implementation; `CONFLICT-003-SEC` Owner SECURITY — adversarial invariant/review; `CONFLICT-003-QA` Owner QUALITY — deterministic cross-platform integration verification.
- Required owner/arbitrator: QUALITY arbitration; BACKEND implementation; SECURITY review.
- Status: RESOLVED.
- Last check: 2026-08-24 on candidate SHA `31b580609527f828b87854207bd1c33c3a4bfec6`.
- Full-Gate link: none yet; promote/cross-link only if this becomes a required-gate blocker.

## CONFLICT-004 — Full-gate UI evidence references non-existent repository paths

- Type: Evidence / ownership-assignment conflict.
- Evidence: `full_gate_recovery.md` assigns UI-owned P0 slices `FGATE-010` and `FGATE-013` from run #2940 to `src/athena/ui/rich_chat.py`, `main_window.py`, `assistant_shell.py`, `persistence.py`, `settings_panel.py`, and `thumbnail_grid.py`. Fresh repository reads show that `src/athena/ui/` does not exist on `agent/pathena` HEAD `ee3d606d7a03a46c112e021e26cec0a2b6ce73e9`, the #2940 head `c59778dcd90b11dd8ee2176b381db0af06848725`, PR #5 base `7dd3b5598b323af11aeb36e1f553c413bd2620b5`, PR #2 base `3e57e70ee2e1bab1d3bb3cf667f22c445c0d1675`, or PR #5 merge commit `f173ceaf719ca33a441a237619592be149884d56`. The productive UI tree on `agent/pathena` is `src/athena/desktop/`.
- Affected IDs/files: `FGATE-010`, `FGATE-013`, `docs/agent_coordination/full_gate_recovery.md`, run #2940 / job `97317379431`, PR #5 gate carrier.
- Side A: QUALITY recovery SSOT assigns two P0 product fixes to UI with exact stack/module paths and asks UI to implement them first.
- Side B: UI can neither reproduce nor patch those paths from any cited repository ref without inventing a second UI architecture or mutating unrelated desktop code.
- Risk: fabricated product files, fixes against the wrong UI architecture, false P0 closure, or unnecessary churn in the real `src/athena/desktop/` implementation.
- Proposed resolution: QUALITY must attach the decoded #2940 diagnostic/stack artifact with its actual checkout/merge SHA or correct `FGATE-010`/`FGATE-013` to repository paths that exist on the cited candidate. Until then UI treats those two slices as evidence-blocked and does not fabricate a product fix. If the evidence came from a stale/unrelated checkout, reclassify the entries `STALE`; if corrected evidence identifies real `src/athena/desktop/` paths, UI resumes the P0 immediately.
- Required owner/arbitrator: QUALITY for evidence correction/reclassification; UI resumes implementation only after a reproducible UI path is supplied.
- Status: OPEN.
- Last check: 2026-08-24 on `agent/pathena` HEAD `ee3d606d7a03a46c112e021e26cec0a2b6ce73e9`; exact-head gate #2941 is completed `failure`, so CI Quiet Mode is not active.
- Full-Gate link: `FGATE-010` / `FGATE-013` ↔ `CONFLICT-004`.

## CONFLICT-005 — Full-gate BACKEND evidence does not match cited source tree

- Type: Evidence / ownership-assignment conflict.
- Evidence: `full_gate_recovery.md` assigns BACKEND P0/P1 slices from run #2940 to diagnostics that cannot be reproduced against the cited branch/source. `FGATE-012` names `src/athena/research/assistant.py`, `src/athena/analysis/capabilities.py`, and `src/athena/restart_scenarios.py`, but fresh reads on current `agent/pathena` return no such files. `FGATE-004`/`FGATE-005` describe strict-typing failures in code that is not present in the corresponding current/cited blobs; for example `research/idempotency.py` and `retrieval/semantic.py` already contain materially different guarded implementations. Backend therefore cannot safely infer the intended patch from the recovery summary alone.
- Affected IDs/files: `FGATE-003`, `FGATE-004`, `FGATE-005`, `FGATE-011`, `FGATE-012`, `docs/agent_coordination/full_gate_recovery.md`, run #2940 / job `97317379431`.
- Side A: QUALITY recovery SSOT marks these BACKEND slices P0/P1 and requires exact reproduction/root-cause fixes.
- Side B: BACKEND cannot map several diagnostics to the cited/current repository tree without fabricating missing modules or altering unrelated replacement code.
- Risk: fixing the wrong implementation, recreating stale files, false P0 closure, or regressing already-reworked Backend code to satisfy diagnostics from another checkout.
- Proposed resolution: QUALITY must publish the raw Ruff/mypy diagnostics with the exact checkout/merge SHA and tree provenance used by #2940, then either correct the affected paths/line references or reclassify stale entries. Until reproducible evidence exists, BACKEND treats only these affected recovery slices as evidence-blocked and continues independent BACKEND P1 work.
- Required owner/arbitrator: QUALITY for evidence correction/reclassification; BACKEND resumes the affected recovery slice immediately once exact reproducible source evidence is supplied.
- Status: OPEN.
- Last check: 2026-08-24 on `agent/pathena` HEAD `b91ca55be92763a7a7a931347eab8241a5861d61`; no exact-head QUEUED/IN_PROGRESS Pflicht-Gate was evidenced through the available connector surface.
- Full-Gate link: `FGATE-003` / `FGATE-004` / `FGATE-005` / `FGATE-011` / `FGATE-012` ↔ `CONFLICT-005`.

## Bot configuration recommendations

No automation prompt was changed by another bot in this file. Evidence-backed recommendations, when any arise, must be reported as `BOT-CONFIG-CHANGE-RECOMMENDED` rather than applied automatically.
