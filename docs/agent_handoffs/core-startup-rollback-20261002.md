# Core startup rollback hardening — 2026-10-02

## Ausgangslage

`AthenaApplication.start()` starts the registered `ServiceManager` before persistent
JSONL setup, News bootstrap, and startup maintenance. If any of those later steps
raised, the exception path changed application state and closed JSONL logging but
did not stop services that had already started.

`ServiceManager.stop_all()` also removed a service from its internal started set
before calling `stop()`. A failing stop was therefore forgotten, so later cleanup
attempts could report success without retrying the still-unreleased service.

A third gap existed before that transactional block: `configure_logging()` ran while
the application was already marked `STARTING`, but outside the startup `try`. A
configuration failure could therefore strand lifecycle state in `STARTING`.

## Root Cause

Two lifecycle ownership gaps composed:

1. application-level startup was only transactional inside `ServiceManager.start_all()`;
   failures after that boundary had no service rollback;
2. service shutdown failure tracking was destructive, so failed releases were not
   retryable by `AthenaApplication.stop()` / `CoreDomainExecutor` cleanup;
3. logging initialization was outside the application startup failure boundary.

This matters most for long-lived integration services such as the optional Obsidian
watcher and for storage ownership during Core startup failure.

## Änderungen

- `AthenaApplication.start()` now includes logging initialization in the same handled
  startup boundary and calls `self.services.stop_all()` on every handled startup
  exception before publishing FAILED / RECOVERY_REQUIRED state.
- rollback failures are logged as `core.start_rollback_failed` but do not replace
  the original startup exception.
- `ServiceManager` now retains services whose `stop()` raised and restores them in
  original start order; a later `stop_all()` retries them in the same reverse-order
  shutdown sequence.
- focused regressions cover:
  - late News-bootstrap failure after a service started;
  - rollback stop failure without loss of the primary startup error;
  - retained failed service identity;
  - successful retry after a transient stop failure;
  - logging configuration failure transitions to `FAILED` instead of remaining
    stranded in `STARTING`.

## Dateien

- `src/athena/core/application.py`
- `src/athena/core/services.py`
- `tests/unit/test_application_startup_rollback.py`
- `tests/unit/test_service_manager.py`
- this handoff

## Verhalten danach

A Core startup that fails after lifecycle services have started no longer leaves
those services running by default. If a service itself cannot stop, that fact stays
tracked for the executor/application cleanup path instead of being silently lost.

The original startup exception remains the surfaced failure; cleanup failure is
additional diagnostic evidence rather than a replacement error.

## Validierung

Local repository checkout is unavailable in this runner because `github.com` DNS
resolution fails. No local pytest/ruff/mypy PASS is claimed.

Validation source for this branch is the exact-head GitHub CI triggered by the draft
PR. Update this handoff with concrete run/job results before merge.

## Abhängigkeiten / Parallelität

Original base: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`.

During this run Develop advanced through merged Chat cancellation PR #329 to
`467ef434236c320e4afe9d21a39c20a4a2b75728`. A compare proved those 31 commits did
not touch this slice's Core lifecycle files. The branch was then synchronized with a
history-preserving two-parent merge commit `ed874185dce4dd9d850d829386e0cf35be19f7aa`;
no force-push or foreign-history rewrite was used.

At synchronization time, fresh parallel PRs owned Chat, Jobs, Knowledge, Sources,
Windows packaging, LM Studio, Backup, Security, Memory, Logging, Settings and PALLAS.
No active PR found by title/body search claimed `src/athena/core/application.py` or
`src/athena/core/services.py`.

PR #353 changes desktop helper lifecycle and is conceptually adjacent, but its body
states its code scope is the six helper CLI files. This branch does not modify those
files.

## Konfliktrisiko

Low-to-moderate. The two Core lifecycle files are central, so any later integration
branch that also changes application/service lifecycle should rebase and rerun the
focused lifecycle tests. No broad refactor was performed.

## Nächste sinnvolle Schritte

1. Review exact-head Quality Gate output, especially Ruff and the two focused unit
   files.
2. If Quality is green, inspect any canonical Windows/focused workflow that GitHub
   attaches to the PR; this change is headless Core lifecycle and should not require
   a visual baseline update.
3. Before merge, compare the PR against the then-current `develop/pathena-next` and
   confirm #353 or other lifecycle work has not begun touching the same Core files.
4. After integration, exercise an injected post-ServiceManager startup failure in a
   Windows/Core smoke environment if available, confirming no child integration
   service survives process startup failure.

## Branch / commits

Branch: `fix/core-startup-rollback-20261002-sol`

Implementation / synchronization commits:
- `42e017f5088606d562c408ff8a4cc0f1d6a08e4a` — application startup rollback
- `11c2528ef0b56eada03aa593a3e9999042976b0b` — startup rollback regression tests
- `9c319edc792a81cc784c30d41e95c6ae6496573f` — retain failed services for retry
- `f84919f143ca01cacf479c7496eb8065993da294` — ServiceManager retry regression
- `35b0b898e67e49d71a83978e6e9a91798fb367f0` — align rollback failure expectation

Additional commits:
- `ed874185dce4dd9d850d829386e0cf35be19f7aa` — synchronize with current Develop without force-push
- `972e95276f62e70944180211d66bce5b0ab042d4` — include logging setup in startup failure boundary
- `e5b4771c29de9dc34d16c6a3819fc219d53bd6a7` — logging-setup failure regression
- `796c5f2d67c6324ebfe6ed148f26aa2c49211922` — document retryable service ownership contract

## Real-service compatibility check

The retry contract was checked against current lifecycle implementations. In
particular, `ObsidianVaultWatchService.stop()` can legitimately raise when its thread
does not exit before the deadline while keeping the thread reference/state available
for a later retry. `StorageBootstrapService` likewise keeps its internal started flag
until database and layout shutdown both complete. Retaining failed services in
`ServiceManager` therefore matches real ownership semantics rather than only a test
fake.
