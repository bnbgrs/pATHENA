# pATHENA Release / Integration Readiness

Lead-owned read-mostly integration record. `main` is read-only. Evidence is SHA-bound and is never transferred silently to a newer candidate.

## Current snapshot

- Updated: 2026-08-25 19:44 Europe/Berlin
- `main`: `3e57e70ee2e1bab1d3bb3cf667f22c445c0d1675`
- accepted `agent/pathena`: `fbbf44dc8c8175499528f07be079061b644d1604`
- `bot/pathena-candidate`: `0103db3d0708a534ff1a6dc6799e60bf850987ce`
- `bot/pathena-coordination`: `7fdb8c07616199b5b49ae6036f309b8abbfbed55` before this record update
- candidate distance from accepted `agent/pathena`: 140 commits ahead, 0 behind

## RC status

`PREPARING`

The candidate remains moving. No RC SHA is frozen. Candidate is materially ahead of accepted `agent/pathena`; exact Quality/Windows evidence and Eleven-screen P1 closure take precedence over noncritical feature churn.

## Readiness checklist

| Area | Status | Exact evidence / reason |
| --- | --- | --- |
| Canonical Quality | PENDING | run `32878905862` is exact-SHA bound to `0103db3...` but has not started jobs yet |
| Targeted tests | PENDING | TASK-0017 restored handle-bound Windows publication at `7487942...`; TASK-0040 adds signed-URL redaction tests through `0103db3...`; required exact system evidence is still pending |
| Promotion guard/readiness | PASS | candidate-bound promotion-readiness run `32878901059` succeeded on `0103db3...`; this is guard evidence, not release acceptance |
| Windows/runtime | PENDING | exact Full-Windows run `32879015256` requested for `0103db3...`; no job has started yet |
| Packaging | PENDING | bundled into exact Full-Windows run `32879015256`; do not inherit older package greens |
| Storage/recovery | PENDING | TASK-0017 validating; TASK-0034 schema migration regression active; TASK-0018/0019/0020/0036 remain ready |
| Security/privacy | PENDING | TASK-0040 validating signed-URL provenance redaction; TASK-0021/0041/0042 remain ready |
| 11-surface UI/visual | PENDING | harness TASK-0015 remains active; Chat, Palette, SYSTEM and ComfyUI have explicit P1 READY slices; PALLAS keyboard/Inspector acceptance remains active/open |
| Critical user flows | PENDING | exact-candidate acceptance must be rerun after current persistence/security/schema work settles |
| Migrations/schema | PENDING | TASK-0034 active for restart-safe archive replication migration |
| Install/upgrade | PENDING | require exact package/install evidence on a stable candidate/RC SHA |
| Known P0/P1 | FAIL | active P1 durable publication and redesign work plus unresolved schema/security acceptance; no freeze yet |

## Change inventory

| Item | Classification | Notes |
| --- | --- | --- |
| `bot/pathena-candidate` through `0103db3...` | IN_CANDIDATE | moving product integration branch |
| TASK-0017 Windows HANDLE-bound durable publication | IN_CANDIDATE / VALIDATING | restored at `7487942...`; unchanged by later Security commits; exact Full-Windows pending |
| TASK-0040 signed-URL provenance redaction | IN_CANDIDATE / VALIDATING | code + adversarial tests landed through `0103db3...`; exact Full-Windows pending |
| TASK-0034 archive replication migration restart safety | PENDING_INTEGRATION | Backend claim active; schema/persistence slice requires exact Full-Windows when landed |
| TASK-0039 PALLAS keyboard navigation | PENDING_INTEGRATION | UI claim active; do not let this displace reference-screen closure |
| TASK-0015 11-surface visual harness | PENDING_INTEGRATION | QA claim active; heartbeat is old and requires explicit owner refresh/takeover before mutation |
| TASK-0043 Chat reference closure | PENDING_INTEGRATION | P1 UI READY |
| TASK-0044 Command Palette reference closure | PENDING_INTEGRATION | P1 UI READY |
| TASK-0045 ComfyUI reference closure | PENDING_INTEGRATION | P1 UI READY |
| TASK-0046 SYSTEM reference closure | PENDING_INTEGRATION | P1 UI READY |
| Cloud-Windows / screenshot / preview / packaging carrier branches | EXCLUDE_TEMPORARY | evidence carriers only unless separately reviewed product changes are identified |
| historical bootstrap/slice-gate workflows from old main lineage | STALE / EXCLUDE_TEMPORARY | must not be revived by blind merge/rebase |

## Merge order

1. Finish exact Full-Windows validation for `0103db3...`; if green, close TASK-0017 and TASK-0040 only with SHA-bound evidence.
2. Resolve active TASK-0034 schema migration regression and run the required persistence Windows/package acceptance on the resulting stable SHA.
3. Refresh or formally reclaim stale TASK-0015 ownership, finish the candidate-bound 11-surface harness, then validate P1 reference-screen slices.
4. Close Chat, Command Palette, SYSTEM, ComfyUI and PALLAS/Inspector reference acceptance in small non-overlapping UI slices.
5. Resolve remaining P1 storage/security slices needed for freeze, notably TASK-0018 and filesystem identity consumers.
6. Select one explicit RC SHA only after P0/P1 closure; run canonical Quality + exact Full-Windows/package + 11-surface validation on that exact SHA.
7. Present the frozen, validated RC for user merge decision. Never merge `main` automatically.

## Conflicts / risks

- Candidate is 140 commits ahead of accepted `agent/pathena`; promotion debt is now material.
- Current Quality and Full-Windows runs are queued/pending; absence of jobs is not PASS evidence.
- `main` contains legacy bootstrap/slice-gate lineage intentionally excluded from candidate; blind main-to-candidate merge/rebase remains unsafe.
- TASK-0017 changes Windows durable publication and TASK-0040 changes durable provenance secrecy; both require fresh exact Windows/runtime/package evidence.
- TASK-0034 is a schema migration regression and can invalidate earlier storage/recovery evidence once it lands.
- TASK-0015 and TASK-0039 have exceeded the normal 90-minute heartbeat window; they remain claims until a documented STALE/TAKEOVER or owner heartbeat occurs.
- Eleven-screen redesign remains incomplete; old `agent/pathena` UI is not the visual target.
- Real RX-7900-XTX/driver/LM-Studio inference remains target-hardware evidence, not cloud evidence.

## Last known good

- Promotion guard/readiness: PASS on `0103db3...`, run `32878901059`.
- Canonical Quality for current candidate: PENDING, run `32878905862`.
- Full Windows/runtime for current candidate: PENDING, run `32879015256`.
- Packaging for current candidate: PENDING in the same exact Full-Windows acceptance.
- 11-surface visual for current candidate: PENDING; TASK-0015 is not completed.
- Older greens are historical only and are not promoted to `0103db3...`.

## Branch hygiene

After a successful future promotion, likely archive/delete candidates include temporary Cloud-Windows, screenshot, preview, packaging and verification-carrier branches. Do not delete branches without explicit user authorization. Preserve product/evidence history until promotion is complete.

## Next RC actions

1. Resolve exact Full-Windows run `32879015256` and canonical Quality run `32878905862` for `0103db3...`; classify failures before additional noncritical churn.
2. Close TASK-0017 and TASK-0040 only if exact required evidence is green; otherwise keep claims open with precise failure handoffs.
3. Finish TASK-0034 restart-safe archive replication migration and re-run persistence/package evidence on its exact resulting SHA.
4. Refresh/reclaim TASK-0015 and make the 11-surface harness authoritative for reference acceptance.
5. Execute P1 reference closures TASK-0043 through TASK-0046 plus PALLAS/Inspector acceptance without secondary UI feature displacement.
6. Reduce remaining P1 storage/security blockers, then select one explicit RC SHA and validate only that SHA.

## Decision log

- 2026-08-25 — `6f8bfac...`: RC remained `PREPARING`; active persistence/security/UI work prevented freeze.
- 2026-08-25 — `3e57e70...` main: keep `main` read-only and never blind-merge/rebase its legacy bootstrap/slice-gate lineage into candidate.
- 2026-08-25 — redesign: incomplete Eleven-screen matrix remains P1 until all named references have exact candidate render/test acceptance.
- 2026-08-25 — `0103db3...`: candidate is 140 ahead/0 behind accepted `agent/pathena`; promotion/readiness guard is green but canonical Quality and exact Full-Windows are still pending, so RC stays `PREPARING`.
- 2026-08-25 — backlog: explicitly reserve P1 UI slices for Chat, Command Palette, ComfyUI and SYSTEM so reference-screen closure outranks secondary UX feature work.
