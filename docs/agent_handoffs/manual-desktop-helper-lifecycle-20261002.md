# Desktop helper lifecycle isolation — 2026-10-02

## Ausgangslage

The native desktop uses short-lived Python helper processes for canonical-memory,
Jobs, Knowledge, Research, ResearchResult and Sources operations. Each helper
constructed `AthenaApplication` and then called
`app.start(run_startup_maintenance=False)`.

That flag skips startup maintenance only. It does **not** make Core startup
read-only or helper-scoped.

## Root cause

`AthenaApplication.start()` owns the global Core lifecycle:

1. performs the canonical database preflight;
2. starts `StorageBootstrapService`;
3. starts `ProtectedContentService`;
4. starts `SourceProtectionTransitionService` and recovery;
5. may start the Obsidian vault watcher when configured;
6. configures persistent Core logging;
7. explicitly calls `NewsService.start()`.

`NewsService.start()` runs schema/default bootstrap inside SQLite write
transactions. Therefore even a read-only desktop helper command such as Jobs
`list` or Knowledge `show` could start unrelated global services and perform
cross-subsystem writes.

The helper modules already receive all required composed repositories/services
from `AthenaApplication.__init__`; their command work only requires the
canonical storage/database lifecycle to be open.

## Changes

All six internal desktop helper entry points now start/stop only
`app.storage_bootstrap` around the existing command implementation:

- `src/athena/desktop/canonical_memory_cli.py`
- `src/athena/desktop/jobs_cli.py`
- `src/athena/desktop/knowledge_cli.py`
- `src/athena/desktop/research_cli.py`
- `src/athena/desktop/research_results_cli.py`
- `src/athena/desktop/sources_cli.py`

No command semantics, repository calls, transition rules, output protocol, job
payloads, Source ingestion behavior, Knowledge acceptance behavior, Research
promotion behavior, or UI layout changed.

`tests/unit/test_desktop_helper_lifecycle.py` covers every helper and asserts:

- full `AthenaApplication.start()` is never called;
- full `AthenaApplication.stop()` is never called;
- storage bootstrap starts exactly once;
- storage bootstrap stops exactly once;
- storage cleanup still occurs when the command raises;
- storage shutdown failure is surfaced as a helper error instead of a false Exit 0.

## Behavior after

A desktop helper still opens the canonical SQLite/storage runtime needed by its
existing service graph, but it no longer impersonates a second global Core
instance. The long-lived Core process remains the owner of News bootstrap,
protection-transition recovery, Obsidian watcher lifetime and global Core
logging.

The helper entry points also no longer swallow `storage_bootstrap.stop()`
failures. Command failure and cleanup failure both leave the process at Exit 2;
a successful command whose cleanup fails is therefore not reported as success.

## Parallel work / conflict risk

During this run, PR #344 (`fix/jobs-protocol-truth-20261002-sol`) appeared and
claimed:

- `src/athena/desktop/jobs_lifecycle.py`
- `src/athena/desktop/jobs_workspace.py`
- `tests/unit/test_pathena_jobs_lifecycle.py`

An earlier scratch branch from this run,
`fix/jobs-runtime-observability-20261002-sol`, had touched the first two files.
It is **superseded and must not be integrated**. No PR is opened from that
scratch branch.

The integration candidate was rebuilt fresh from
`develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b` as
`fix/jobs-helper-lifecycle-20261002-sol`. It does not modify any #344-owned
file.

Other active Chat, LM Studio, Settings/News, Sources import queue, Windows
packaging, Obsidian, Backup, Model and Update PR file sets were rechecked before
this broader helper-lifecycle change; none owns these six CLI files or the new
focused test.

## Validation

Local checkout/pytest execution is unavailable in the current execution
environment because direct github.com DNS access fails. No local PASS is
claimed.

Performed before PR:

- exact branch/develop comparison;
- branch is 0 commits behind current Develop at comparison time;
- final candidate changes only the six helper entry points, one focused test and
  this handoff;
- >100-character and trailing-whitespace checks are clean for the initially
  modified Jobs slice; exact CI remains authoritative for the full candidate.

Required exact-head validation:

1. focused `tests/unit/test_desktop_helper_lifecycle.py`;
2. Ruff;
3. mypy for source changes;
4. canonical ATHENA Quality Gate;
5. Windows package gate if the repository PR policy selects it.

## Result / remaining risks

Implementation is complete but not yet CI-verified. Exact-head CI was queued
for PR #353 after the final product/test changes.

The change deliberately preserves `StorageBootstrapService.start()`, because
the helpers still require canonical storage layout, migration/preflight and live
SQLite ownership. This is not a read-only-storage redesign.

If any helper is later extended to depend on a lifecycle-managed service beyond
storage, that dependency must be attached explicitly rather than restoring
full `AthenaApplication.start()`.

## Next owner

Integrator/QA:

1. require exact-head green focused + canonical Quality evidence;
2. verify #344 independently and merge/order it without combining its
   Jobs-protocol files into this slice;
3. integrate this helper-lifecycle slice only if its final diff remains
   disjoint from concurrent PRs.
