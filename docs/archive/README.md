# Historical agent-run evidence

This directory is the durable pointer for historical development-run material removed from the active documentation tree during repository hygiene.

## Archived snapshot

- Source branch: `bot/pathena-candidate`
- Snapshot commit: `5b1438e585b1e6d758132e1d5df3adad68a49adf`
- Archived paths:
  - `docs/agent_logs/`
  - `docs/agent_backend_run_101_200.md`
  - `docs/agent_backend_run_201_300.md`
  - `docs/QA/ATHENA_REPOSITORY_QA_2026-08-10.md`

The complete original files remain recoverable from Git history at the snapshot commit above.

`docs/quality-gate/` is intentionally retained because the active Quality queue still references individual evidence files there. No runtime, source, test, workflow, active queue, security, Alpha/Beta, Windows-local, or currently referenced quality-gate evidence is archived by this change.

## Active sources of truth

Current bot coordination and task state remain under `docs/agent_coordination/`. Referenced gate evidence remains under `docs/quality-gate/`. Security evidence remains under `docs/security/`.

## Hygiene rule

Per-run scratch evidence should not become a permanent source of truth unless an active queue, unresolved regression, security finding, or release decision depends on it. Prefer CI artifacts or temporary run output for raw logs. Persist only compact current status or explicitly referenced durable evidence.

When historical agent-run material is required, recover the exact file from the snapshot commit rather than copying stale run state back into active queues.