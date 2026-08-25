# pATHENA Release / Integration Readiness

Lead-owned read-mostly integration record. `main` is read-only. Evidence is SHA-bound and is never transferred silently to a newer candidate.

## Current snapshot

- Updated: 2026-08-25 20:03 Europe/Berlin
- `main`: `3e57e70ee2e1bab1d3bb3cf667f22c445c0d1675`
- accepted `agent/pathena`: `fbbf44dc8c8175499528f07be079061b644d1604`
- `bot/pathena-candidate`: `7215fe1ed70ecf5656b29b1f676f143760122c52`
- candidate distance from accepted `agent/pathena`: 145 commits ahead, 0 behind

## RC status

`PREPARING`

No RC SHA is frozen. Candidate is materially ahead of accepted `agent/pathena`; exact Quality/Full-Windows evidence, active persistence/schema/security closure and Eleven-screen P1 acceptance take precedence over noncritical feature churn.

## Readiness checklist

| Area | Status | Exact evidence / reason |
| --- | --- | --- |
| Canonical Quality | PENDING | last requested Quality run `32878905862` is bound to older `0103db3...`; recheck required on a settled current SHA |
| Targeted tests | PASS | reserve-pressure contract `32880698392` PASS on `7215fe1...`; corrected exact durable-FS contract `32881150977` PASS with immutable SHA, Ruff, Mypy and native Windows tests including parent-replacement race |
| Promotion guard/readiness | RECHECK_NEEDED | run `32878901059` passed on older `0103db3...`; candidate has moved |
| Windows/runtime | PENDING | full exact-current acceptance run `32880698289` is pending behind older canonical run `32878181122` on `7487942...`, which remains stuck in packaged worker dispatch |
| Packaging | PENDING | no exact `7215fe1...` full package/cold-start acceptance yet |
| Storage/recovery | PENDING | TASK-0017 targeted evidence is green but full Windows/package remains required; TASK-0034 schema migration slice is in candidate and claim/evidence remains active; TASK-0018/0019/0020/0036 remain ready |
| Security/privacy | PENDING | TASK-0040 signed-URL redaction is in candidate and awaiting exact system evidence; TASK-0021/0041/0042 remain ready |
| 11-surface UI/visual | PENDING | TASK-0015 remains active; Chat, Palette, SYSTEM and ComfyUI have explicit P1 READY slices; PALLAS keyboard/Inspector acceptance remains open |
| Critical user flows | PENDING | exact-candidate acceptance must be rerun after current persistence/schema/security work settles |
| Migrations/schema | PENDING | TASK-0034 changes are in candidate; owner verification/handoff and exact Windows evidence still required |
| Install/upgrade | PENDING | require exact package/install evidence on stable candidate/RC SHA |
| Known P0/P1 | FAIL | active P1 durable-publication/redesign work plus schema/security acceptance prevents freeze |

## Change inventory

| Item | Classification | Notes |
| --- | --- | --- |
| `bot/pathena-candidate` through `7215fe1...` | IN_CANDIDATE | moving product integration branch |
| TASK-0017 Windows HANDLE-bound durable publication | IN_CANDIDATE / VALIDATING | Win32 relative `SetFileInformationByHandle` produced Error 87 on Windows Server 2025; candidate now uses native `NtSetInformationFile(FileRenameInformation)` with bound destination-parent HANDLE. Exact targeted Windows contract is green; full acceptance still pending |
| TASK-0040 signed-URL provenance redaction | IN_CANDIDATE / VALIDATING | code + adversarial tests landed before current SHA; exact full-system evidence pending |
| TASK-0034 archive replication migration restart safety | IN_CANDIDATE / VALIDATING | Backend schema/migration changes landed before `7215fe1...`; claim remains active pending owner evidence |
| TASK-0039 PALLAS keyboard navigation | PENDING_INTEGRATION | UI claim active; must not displace reference-screen closure |
| TASK-0015 11-surface visual harness | PENDING_INTEGRATION | QA claim heartbeat is stale; no silent takeover performed |
| TASK-0043 Chat reference closure | PENDING_INTEGRATION | P1 UI READY |
| TASK-0044 Command Palette reference closure | PENDING_INTEGRATION | P1 UI READY |
| TASK-0045 ComfyUI reference closure | PENDING_INTEGRATION | P1 UI READY |
| TASK-0046 SYSTEM reference closure | PENDING_INTEGRATION | P1 UI READY |
| Cloud-Windows / screenshot / preview / packaging carrier branches | EXCLUDE_TEMPORARY | evidence carriers only unless separately reviewed product changes are identified |
| historical bootstrap/slice-gate workflows from old main lineage | STALE / EXCLUDE_TEMPORARY | must not be revived by blind merge/rebase |

## Merge order

1. Keep TASK-0017 open until pending exact full-Windows run `32880698289` (or a later stable-SHA replacement) completes runtime/package/cold-start acceptance.
2. Obtain Backend handoff for TASK-0034 and classify schema-related system failures separately from TASK-0017.
3. Close TASK-0040 only with its required exact full-system evidence.
4. Refresh or formally reclaim stale TASK-0015 ownership, finish candidate-bound 11-surface harness, then validate P1 reference-screen slices.
5. Close Chat, Command Palette, SYSTEM, ComfyUI and PALLAS/Inspector reference acceptance in small non-overlapping UI slices.
6. Resolve remaining P1 storage/security blockers, select one explicit RC SHA, and run canonical Quality + exact Full-Windows/package + 11-surface validation only on that SHA.
7. Present frozen validated RC for user merge decision; never merge `main` automatically.

## Conflicts / risks

- Candidate is 145 commits ahead of accepted `agent/pathena`; promotion debt is material.
- Exact full-Windows evidence for `7215fe1...` is pending behind an older acceptance run stuck in packaged worker dispatch; older SHA evidence cannot be promoted to current candidate.
- `main` contains legacy bootstrap/slice-gate lineage intentionally excluded from candidate; blind main-to-candidate merge/rebase remains unsafe.
- TASK-0017 touches Windows durable publication; TASK-0034 touches schema migration; TASK-0040 touches durable provenance secrecy. A current exact full-system acceptance is mandatory before freeze.
- TASK-0015 and TASK-0039 have exceeded the normal 90-minute heartbeat window; they remain claims until documented STALE/TAKEOVER or owner heartbeat.
- Eleven-screen redesign remains incomplete; old `agent/pathena` UI is not the visual target.
- Real RX-7900-XTX/driver/LM-Studio inference remains target-hardware evidence, not cloud evidence.

## Last known good

- Reserve-pressure Windows contract: PASS on `7215fe1...`, run `32880698392`.
- Durable-FS exact Windows contract: PASS on `7215fe1...`, run `32881150977` (immutable checkout, Ruff, Mypy, native Windows tests including bound-parent replacement race).
- Promotion guard/readiness for current candidate: RECHECK_NEEDED; previous PASS was on `0103db3...`.
- Canonical Quality for current candidate: UNKNOWN/PENDING.
- Full Windows/runtime/package for current candidate: PENDING, run `32880698289` waiting behind older run `32878181122`.
- 11-surface visual for current candidate: PENDING.

## Branch hygiene

After a successful future promotion, likely archive/delete candidates include temporary Cloud-Windows, screenshot, preview, packaging and verification-carrier branches. Do not delete branches without explicit user authorization. Preserve product/evidence history until promotion is complete.

## Next RC actions

1. Let pending exact Full-Windows run `32880698289` execute after the older canonical run releases the concurrency slot; classify runtime/package failures precisely.
2. Close TASK-0017 only when its required full-system evidence is green; targeted Windows evidence is already complete.
3. Obtain TASK-0034 Backend handoff and TASK-0040 Security handoff; re-run canonical Quality and promotion readiness on the same stable candidate SHA.
4. Refresh/reclaim TASK-0015 and make the 11-surface harness authoritative for reference acceptance.
5. Execute P1 reference closures TASK-0043 through TASK-0046 plus PALLAS/Inspector acceptance.
6. Reduce remaining P1 storage/security blockers, then select one explicit RC SHA and validate only that SHA.

## Decision log

- 2026-08-25 — `6f8bfac...`: RC remained `PREPARING`; active persistence/security/UI work prevented freeze.
- 2026-08-25 — `3e57e70...` main: keep `main` read-only and never blind-merge/rebase its legacy bootstrap/slice-gate lineage into candidate.
- 2026-08-25 — redesign: incomplete Eleven-screen matrix remains P1 until all named references have exact candidate render/test acceptance.
- 2026-08-25 — `0103db3...`: candidate was 140 ahead/0 behind accepted `agent/pathena`; guard evidence passed but was invalidated for release-readiness purposes when candidate moved.
- 2026-08-25 — backlog: explicitly reserved P1 UI slices for Chat, Command Palette, ComfyUI and SYSTEM so reference-screen closure outranks secondary UX feature work.
- 2026-08-25 — `7215fe1...`: Windows Server 2025 empirically rejected Win32 relative `SetFileInformationByHandle` rename with Error 87, while native `NtSetInformationFile(FileRenameInformation)` with the same bound parent HANDLE succeeded; candidate was corrected to native handle-relative publication.
- 2026-08-25 — `7215fe1...`: exact targeted durable-FS contract `32881150977` passed immutable checkout, Ruff, Mypy and native Windows behavior; TASK-0017 remains open solely because full runtime/package acceptance is still pending.
