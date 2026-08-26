# Historical agent and quality-gate evidence

This directory is the durable pointer for historical development-run evidence that was removed from the active documentation tree during repository hygiene.

## Archived snapshot

- Source branch: `bot/pathena-candidate`
- Snapshot commit: `5b1438e585b1e6d758132e1d5df3adad68a49adf`
- Archived paths:
  - `docs/agent_logs/`
  - `docs/quality-gate/`
  - `docs/agent_backend_run_101_200.md`
  - `docs/agent_backend_run_201_300.md`
  - `docs/QA/ATHENA_REPOSITORY_QA_2026-08-10.md`

The complete original files remain permanently recoverable from Git history at the snapshot commit above. No runtime, source, test, workflow, active queue, security, Alpha/Beta, or Windows-local documentation is archived by this change.

## Active sources of truth

Current bot coordination and task state remain under `docs/agent_coordination/`. Security evidence remains under `docs/security/`. Product and platform documentation remains in its existing active locations.

## Hygiene rule

Per-run scratch evidence should not become a permanent source of truth. Prefer CI artifacts or temporary run output for raw logs. Persist only a compact current status, durable investigation result, or evidence that is explicitly required for an unresolved task, regression, security finding, or release decision.

When historical evidence is required, recover the exact file from the snapshot commit rather than copying stale run state back into active queues.