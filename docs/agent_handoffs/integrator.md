# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-11T10:50Z
Branch: `develop/pathena-next`
Run-start HEAD: `ccfbeb620cf009b75c6c53e5821438bf869ab114`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Exact Develop canonical Quality `34586893958@ccfbeb620cf009b75c6c53e5821438bf869ab114 = SUCCESS` before this mutation.
- Immediately before mutation, Develop had zero queued and zero in-progress workflow runs.
- Current worker heads reviewed: Errors `d16707612361e46849b326e1a207612f9e3ba2ad`; Spec/Core `0d7e6281a584a302350a6b3aea0ac63e6eac744a`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `199f123f893251b9fc6984e78c24f9ab5813cdc8`.
- Spec/Core relation-registry behavior is already integrated on Develop; do not reintegrate it.
- Errors reports `ERR-0033/BE-046` and `ERR-0035/BE-052` as Backend-owned OPEN gaps; Backend still has no tested bounded product candidate.
- UI candidate `199f123f893251b9fc6984e78c24f9ab5813cdc8` is bounded to the Sources inspector context plus its focused test and evidence docs. Exact Windows visual run `34580743951` captured all eleven surfaces successfully and failed only at the fail-closed visual verdict because no approved committed baseline exists. However that worker lineage used an older visual workflow and did not execute `tests/unit/test_pathena_navigation_context_accessibility.py`, so the candidate is not yet READY.
- A direct local focused-test attempt from this integrator environment was blocked before checkout by DNS resolution of `github.com`; no fabricated local PASS is claimed.
- `docs/agent_logs/ERROR_LEDGER.md` exists but its Develop baseline metadata is historical/stale and is not authoritative for current OPEN state.
- No `ALPHA_BETA_PROGRESS.md` exists in the repository search result; no synthetic completion percentage is recorded.
- Visual source of truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; no screenshot-level `MATCH` is claimed.

## Tooling unblocker integrated this run

Added `.github/workflows/ui-focused-candidate.yml` as a develop-owned pull-request verification lane for UI candidates targeting `develop/pathena-next`.

The lane resolves `github.event.pull_request.head.sha`, checks out exactly that immutable worker head, proves the checked-out identity, installs the locked Python 3.12 dev+desktop environment, and executes only the focused `tests/unit/test_pathena_navigation_context_accessibility.py` contract on Windows.

This closes the recurring evidence gap caused when `postmerge/ui` carries an older copy of `ui-snapshot.yml`: focused candidate evidence can now be produced from the current Develop-owned workflow definition without weakening the worker visual verdict or changing product code.

No Storage, Recovery, Transport, Runtime, Security, packaging, visual baseline, comparator threshold, test assertion, Skip/XFail, or release guard is weakened.

## Persistent release guards

- pypdf packaging, fail-closed Frozen argv and Desktop/Worker two-EXE topology remain guarded.
- Exactly one Desktop instance with bounded workers remains guarded.
- Adaptive 2048-context Chat reserve remains guarded.
- Windows lane-lock/path-safety and duplicate-column/Core-startup/storage-bootstrap signatures remain protected.
- Historical signatures are not reopened without exact-current reproduction.

## Next integration

1. Consume canonical Quality for this integration SHA before any further Develop mutation.
2. Re-read all worker heads and current handoffs after that gate completes.
3. For the UI Sources candidate, require an exact-head successful focused-candidate run in addition to its existing exact Windows visual capture evidence before promotion.
4. Keep Backend/Storage/Migration/Runtime work conservative until focused current-head adversarial evidence exists.
5. Keep visual `MATCH` claims fail-closed until approved reference/current-render evidence exists.
