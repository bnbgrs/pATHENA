# pATHENA Agent Coordination Protocol

This file and `.pathena/agent-ledger.json` live on branch `bot/pathena-coordination` and are the single coordination authority for the five scheduled pATHENA agents. Product work remains on `bot/pathena-candidate`. Never modify `bnbgrs/ATHENA`.

## Required cycle

1. Read live `bot/pathena-candidate` SHA.
2. Read this protocol and the latest ledger from `bot/pathena-coordination`.
3. Remove nothing from another agent's active claim. A claim is stale only after 90 minutes without a heartbeat, and takeover must be recorded as an event.
4. Select only work inside the agent's role that does not overlap active claim paths or semantic scope.
5. Claim by updating the ledger using the blob SHA just read. The claim must include task id, owner, priority, base candidate SHA, semantic scope, exact/expected file paths, started_at, heartbeat_at and verification plan.
6. If the ledger update fails because its blob SHA is stale, do not force or retry the old content. Re-read the ledger and choose again. This is the atomic collision barrier.
7. Before editing product code, re-read candidate SHA and ledger. If candidate moved in relevant paths or a conflicting claim appeared, abandon/rebase/reselect rather than overwrite.
8. Work only the claimed slice. Do not wholesale-merge stale worker branches.
9. Verify with targeted tests. Add Ruff/Mypy where relevant. Windows/runtime/packaging/UI changes require exact Windows evidence when practical.
10. Review the final diff against the declared scope before publishing candidate changes.
11. Record result, candidate commit SHA, verification evidence, residual risks and useful follow-up tasks in the ledger.
12. Release the claim only after recording outcome. Then, if runtime remains, repeat from step 1.

## Large-ledger / truncated-response recovery

A connector response that truncates `.pathena/agent-ledger.json` is a tooling presentation limit, not by itself a coordination blocker.

1. Retry ledger access once with repository file reads on `bot/pathena-coordination` using bounded `start_line` / `end_line` ranges. Read consecutive non-overlapping chunks until the complete file is reconstructed. Prefer chunks around 80-160 lines and reduce the range if a chunk still truncates.
2. Preserve the exact file order and bytes/line content while reconstructing. Use the blob SHA returned by the file read as the optimistic-lock SHA for any ledger mutation.
3. Immediately before a ledger mutation, re-read the candidate SHA and the ledger region containing active claims relevant to the proposed paths/semantic scope. If the blob SHA changed, discard the reconstructed old ledger and re-read; never force-update.
4. If complete reconstruction cannot be proven, do not mutate the ledger. Do not spend the remainder of the run repeating the same failed full-file read. Continue only inside an already valid, non-conflicting own claim, or perform evidence-producing read-only verification/handoff work and switch to another safe slice that needs no product mutation.
5. A bot must not leave an already completed own claim stale merely because the ledger is large. On the next successful chunked read, closing/releasing that completed claim is the first coordination action before claiming new product paths.
6. Do not treat stale foreign claims as free. The normal 90-minute STALE/TAKEOVER event rule still applies.

## No-idle / blocker rotation rule

- The same unchanged connector/tooling blocker may be diagnosed only once per run.
- After one safe retry or the chunked-ledger recovery above, either make the safe coordination mutation, continue within an existing valid claim, or switch to a different evidence-producing non-conflicting slice.
- Never use tooling limits as a reason for an hour-long repetition of the same read-only root-cause analysis.
- Never bypass claim ownership to create progress. Product mutation still requires a valid claim.

## Claim shape

```json
{
  "task_id": "TASK-0001",
  "owner": "PATHENA-BACKEND",
  "priority": "P1_CORE",
  "status": "CLAIMED",
  "base_candidate_sha": "<40-hex>",
  "scope": "short semantic scope",
  "paths": ["src/athena/..."],
  "started_at": "RFC3339 UTC",
  "heartbeat_at": "RFC3339 UTC",
  "verification": ["specific test or check"]
}
```

## Collision rules

- Path overlap with an active claim is a conflict unless the existing owner explicitly releases or narrows it first.
- Semantic overlap counts even when paths differ (for example two agents changing the same runtime contract through different modules).
- Integration/Lead may coordinate a handoff but should not silently take worker scope.
- A stale claim is not automatically deleted. Record `CLAIM_STALE`, then `CLAIM_TAKEOVER` or `CLAIM_RELEASED` with reason.
- Never force-update the coordination branch to win a race.

## No-work rule

If no useful unclaimed task exists, do not manufacture code churn. Perform an evidence-producing audit, improve tests, or add a well-supported backlog item instead.
