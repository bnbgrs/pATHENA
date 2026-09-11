# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-11T12:49Z
Branch: `develop/pathena-next`
Run-start HEAD: `dfa4a81b4c650339a16be5f60f87804e7cf6a68b`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Exact Develop canonical Quality `34596386099@dfa4a81b4c650339a16be5f60f87804e7cf6a68b = SUCCESS` before this mutation.
- Immediately before mutation, Develop had zero queued and zero in-progress workflow runs.
- Worker heads reviewed: Errors `eaf707a9429b6c67b7d436d64d362b30fac97126`; Spec/Core `2a9b76dd3581cb13052741907d0fad8357553536`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `5e86bf3ab5cd8faaadc44e7dbe1bc2fe9fc76f5a`.
- Current Spec/Core head is not READY: exact canonical Quality `34598764602@2a9b76dd3581cb13052741907d0fad8357553536 = FAILURE`. Full pytest, Linux storage, Windows path/storage/durable-fs/runtime/ownership/packaging/chat-reserve/restart/pypdf guards, and local-install smoke passed; Ruff failed.
- The current Spec/Core delta after its previously exact-green `db8e7d1238320c5aff276472eeee586531530aef` includes the bounded `revision_diff.py` + `test_claim_revision_diff.py` product/test pair, but promotion is held until exact-head lint evidence is green.
- Errors still reports Backend-owned `ERR-0033/BE-046` and `ERR-0035/BE-052`; Backend has no tested bounded product candidate. No Storage mutation is taken here.
- `docs/agent_logs/ERROR_LEDGER.md` exists but its baseline metadata is historical/stale; current error ownership comes from current worker handoffs plus exact-current CI evidence.
- `ALPHA_BETA_PROGRESS.md` remains absent at the requested repository path; no synthetic completion percentage is recorded.
- Visual source of truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; all eleven surfaces remain `IMPLEMENTED_PENDING_VISUAL_REVIEW` and no screenshot-level `MATCH` is claimed without reference/current-render pairing.
- Current UI lineage is not promoted: available exact Windows visual evidence remains fail-closed at the visual verdict without approved baseline/reference pairing, and the latest worker head is not a newly exact-qualified bounded product slice.

## Cross-cutting tooling unblocker integrated this run

Added `.github/workflows/core-focused-candidate.yml` as a Develop-owned exact-PR-head verification lane for Core Knowledge candidates.

The lane resolves and validates the immutable pull-request head SHA and base SHA, checks out exactly the candidate SHA with full history, proves checkout identity, verifies the base commit is available, installs the locked Python 3.12 dev environment, then derives only changed Python files under `src/athena/knowledge/` and `tests/unit/` from the exact PR base-to-head diff.

It runs Ruff only on those changed candidate files and runs pytest on changed `tests/unit/test_*.py` files. This gives workers immediate exact-head focused lint/test diagnostics without replacing or weakening canonical Quality. `cancel-in-progress` is false, so a worker documentation commit must not erase evidence from an already-running candidate check.

No product behavior, Storage, Recovery, Transport, Runtime, Security, packaging, visual baseline, comparator threshold, canonical Quality gate, test assertion, Skip/XFail, or release guard is weakened.

## Persistent release guards

- pypdf packaging, fail-closed Frozen argv, Desktop/Worker two-EXE topology, one Desktop instance with bounded workers, adaptive 2048-context Chat reserve, Windows lane-lock/path-safety, duplicate-column/Core-startup/storage-bootstrap protections remain unchanged.
- Historical signatures are not reopened without exact-current reproduction.

## Next integration

1. Consume canonical Quality for the resulting Develop SHA before any further Develop mutation.
2. Re-read all worker heads and handoffs after that gate completes.
3. Use the new exact-head Core focused lane to qualify the current Spec/Core candidate; do not promote `revision_diff.py` until Ruff plus focused tests are green on an exact candidate head.
4. Keep BE-046/BE-052 conservative until Backend provides a bounded exact-tested candidate.
5. Keep all visual `MATCH` claims fail-closed until approved original-reference and exact-render evidence exists.
