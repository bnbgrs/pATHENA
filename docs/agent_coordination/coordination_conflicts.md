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

## Bot configuration recommendations

No automation prompt was changed by another bot in this file. Evidence-backed recommendations, when any arise, must be reported as `BOT-CONFIG-CHANGE-RECOMMENDED` rather than applied automatically.
