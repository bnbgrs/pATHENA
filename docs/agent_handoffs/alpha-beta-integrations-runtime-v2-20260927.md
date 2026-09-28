# Alpha/Beta Integrations runtime v2 — Obsidian watcher ownership

Date: 2026-09-27
Base Develop: `36e9ec9f2f3e0506c92036e266fc746daba0d75d`
Branch: `fix/alpha-beta-integrations-runtime-v2`

## This slice
- reuses the watcher, stable-ID parser, reconciliation and write stamps integrated by PR #285;
- composes a watcher service only when `projection_root` is explicitly configured;
- gives the watcher deterministic Core start/stop ownership;
- uses a dedicated SQLite connection created and closed inside the watcher thread;
- starts after canonical storage bootstrap and stops before canonical storage shutdown;
- pauses fail closed when the configured vault is missing or unsafe without blocking normal Core startup;
- exposes bounded runtime state, last error and last processed result for later status/conflict presentation;
- preserves the rule that Obsidian remains optional and never owns canonical Knowledge.

## Verification
- Projection/export/import/sync plus Core lifecycle: 33 passed.
- Ruff: passed for all changed Python files.
- mypy: passed for the two changed source modules.
- The runtime test proves self-write suppression, external edit reconciliation into revision 2,
  and clean watcher shutdown using its own thread-local database connection.

## Remaining Beta 20 work
1. durable conflict state and explicit resolution;
2. three-way merge for provably non-overlapping edits;
3. no-ID files as explicit import candidates;
4. delete intent instead of canonical deletion;
5. Protected Content projection policy;
6. UI only after the corresponding runtime states exist.
