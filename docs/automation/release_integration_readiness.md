# pATHENA Release / Integration Readiness

Lead-owned read-mostly integration record. `main` is read-only. Evidence is SHA-bound and is never transferred silently to a newer candidate.

## Current snapshot

- Updated: 2026-08-25 17:57 Europe/Berlin
- `main`: `3e57e70ee2e1bab1d3bb3cf667f22c445c0d1675`
- accepted `agent/pathena`: `fbbf44dc8c8175499528f07be079061b644d1604`
- `bot/pathena-candidate`: `6f8bfacfb88cd3371cdfb509a0aed54713e8b40e`
- coordination baseline before this record: `5f4d614f7d9875bd408b7127237d5089f0dbb403`
- candidate distance from accepted `agent/pathena`: 133 commits ahead, 0 behind

## RC status

`PREPARING`

The candidate is moving. No RC SHA is frozen. Candidate is substantially ahead of accepted `agent/pathena`, so exact QA/Windows evidence and P1 redesign closure take precedence over noncritical feature churn.

## Readiness checklist

| Area | Status | Exact evidence / reason |
| --- | --- | --- |
| Canonical Quality | PENDING | run `32868537963` is pending for candidate `6f8bfacfb88cd3371cdfb509a0aed54713e8b40e` |
| Targeted tests | PENDING | TASK-0017 added handle-bound publication tests on candidate `6f8bfac...`; final task evidence not yet recorded in ledger |
| Windows/runtime | PENDING | TASK-0017 changes Windows durable publication; fresh exact-candidate Full-Windows is required |
| Packaging | PENDING | must be included with fresh Full-Windows after current persistence/process-boundary work settles |
| Storage/recovery | PENDING | TASK-0017 active; TASK-0018/0019/0020 and restart-safe migration TASK-0034 remain open |
| Security/privacy | PENDING | TASK-0038 plugin process boundary active; Windows DACL TASK-0021 remains open |
| 11-surface UI/visual | PENDING | redesign matrix is not fully accepted; Chat, Palette, System and ComfyUI remain open/queued; candidate-bound visual harness TASK-0015 active |
| Critical user flows | PENDING | exact-candidate acceptance must be rerun after current P1 slices |
| Migrations/schema | PENDING | TASK-0034 remains open |
| Install/upgrade | PENDING | require fresh exact-candidate package/install evidence before RC |
| Known P0/P1 | FAIL | active P1 durable-publication slice plus open redesign/P1 readiness work; no freeze yet |

## Change inventory

| Item | Classification | Notes |
| --- | --- | --- |
| `bot/pathena-candidate` through `6f8bfac...` | IN_CANDIDATE | moving product integration branch |
| TASK-0017 Windows handle-bound durable publication | IN_CANDIDATE / VALIDATING | code + tests landed in candidate; ledger still CLAIMED |
| TASK-0038 plugin host/capability broker | IN_CANDIDATE / PENDING_INTEGRATION_EVIDENCE | active Security claim; do not treat process isolation as hostile-code sandbox |
| TASK-0032 Obsidian Knowledge UI | IN_CANDIDATE / PENDING_INTEGRATION_EVIDENCE | active UI claim |
| TASK-0015 11-surface visual harness | PENDING_INTEGRATION | active QA claim |
| Cloud-Windows / screenshot / preview / packaging carrier branches | EXCLUDE_TEMPORARY | evidence carriers only unless a separately reviewed product commit is identified |
| historical bootstrap/slice-gate workflows from old main lineage | STALE / EXCLUDE_TEMPORARY | must not be revived by a blind merge/rebase |

## Merge order

1. Finish and verify TASK-0017; then refresh exact Windows evidence because persistence semantics changed.
2. Close or explicitly hand off active TASK-0038 Security and TASK-0032 UI slices; review diffs against claims.
3. Land/finish TASK-0015 candidate-bound 11-surface harness and use it for remaining reference-screen acceptance.
4. Resolve remaining P1 storage/schema tasks and redesign reference gaps in small verified slices.
5. Select one explicit RC SHA only after P0/P1 closure; run canonical Quality + exact Full-Windows/package + 11-surface validation on that SHA.
6. Present the frozen, validated RC for user merge decision. Do not merge `main` automatically.

## Conflicts / risks

- Candidate is 133 commits ahead of accepted `agent/pathena`; historical evidence on older SHAs is not transferable.
- `main` contains legacy bootstrap/slice-gate lineage that the candidate intentionally removed; a blind main-to-candidate merge/rebase can revive obsolete workflows.
- TASK-0017 modifies Windows durable publication and therefore requires fresh Windows/runtime/package evidence.
- Plugin process isolation is not an OS sandbox; executable third-party loading must remain fail-closed until the Security design is complete.
- Eleven-screen redesign remains incomplete; old `agent/pathena` UI is not the visual target.
- Real RX-7900-XTX/driver/LM-Studio inference remains target-hardware evidence, not cloud evidence.

## Last known good

- Canonical Quality for current candidate: `PENDING` — run `32868537963` on `6f8bfac...`.
- Full Windows/runtime for current candidate: `PENDING` because TASK-0017 changed persistence semantics after prior green evidence.
- Packaging for current candidate: `PENDING` for the same reason.
- 11-surface visual for current candidate: `PENDING`; TASK-0015 is still active.
- Older green runs are historical only and must not be promoted to the current SHA.

## Branch hygiene

After a successful future promotion, likely archive/delete candidates include temporary Cloud-Windows, screenshot, preview, packaging and verification-carrier branches. Do not delete any branch without explicit user authorization. Preserve product/evidence history until promotion is complete.

## Next RC actions

1. Obtain TASK-0017 completion evidence and run the required exact-candidate Full-Windows/package acceptance.
2. Resolve the current canonical Quality run for `6f8bfac...`; diagnose any red lane before adding noncritical churn.
3. Finish TASK-0015 and bind the 11 named reference surfaces to deterministic candidate evidence.
4. Close the remaining queued reference-screen slices: Chat, Command Palette, System, ComfyUI, plus PALLAS/Inspector acceptance.
5. Complete or explicitly defer P1 storage/schema blockers, especially TASK-0018 and TASK-0034.
6. Re-evaluate promotion readiness after 3–5 productive slices or any runtime/network/persistence/process-boundary change.

## Decision log

- 2026-08-25 — `6f8bfac...`: RC remains `PREPARING`. Candidate is moving and contains active persistence/security/UI work; historical greens are not transferred.
- 2026-08-25 — `3e57e70...` main: keep `main` read-only and do not blind-merge/rebase its legacy bootstrap/slice-gate lineage into candidate.
- 2026-08-25 — redesign: treat the incomplete eleven-screen matrix as P1 until all named references have exact candidate render/test acceptance.
