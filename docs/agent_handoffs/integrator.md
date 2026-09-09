# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop baseline for this run: `e1aca469e4e27356f7de14e59ee63171a0d7111b`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `176c3069b16a389cf8d31b6ebe67fc8670ba5bc4`; spec-core `9e0f1df1a0321c2568993f974a4b1dcf316e6b21`; backend `102aecd2c61415b0a428f6e69bba61bd3fb54f0b`; UI `2cb2feb3685358f629095445554c9d04fd56efd1`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update, history rewrite, auto-merge or main promotion was used.

## Exact evidence consumed

- Exact Develop head `e1aca469e4e27356f7de14e59ee63171a0d7111b` had no associated canonical Quality run and no queued/in-progress exact-head gate when mutation eligibility was checked.
- UI exact head `2cb2feb3685358f629095445554c9d04fd56efd1` has canonical Quality `34304620632` in progress. Windows path safety, Linux storage regressions, Local install smoke, specification validator, Ruff and mypy are green; full pytest remains in progress. UI is therefore not READY yet.
- Backend exact head `102aecd2c61415b0a428f6e69bba61bd3fb54f0b` has canonical Quality `34303936995` in progress and remains conservative hold until exact completion.
- Spec/Core current head verifies the already integrated DirectChat boundary lineage; no separate READY product slice was consumed.

## Progress this run — DirectChat budget provenance

No current Worker product slice was READY. A bounded Core-owned cross-cutting provenance improvement records both the user/configuration-requested output reserve and the effective reserve actually authorized after loaded-context adaptation. The existing provider parameter and ContextPackage budget continue to use only the effective reserve, so generation limits and fail-closed context behavior are unchanged.

The configuration recorded in the model signature and ProcessingRun now contains `requested_output_reserve` and `effective_output_reserve` alongside the existing context limit, recent-turn limit and safety margin. This prevents adaptive 2048-context runs from losing the distinction between configured intent and the reduced runtime authorization during later audit/replay analysis.

Focused unit coverage locks the requested/effective distinction. No Skip/XFail was added; no assertion, Security, Storage, Recovery, validator, provider, scheduler/worker, packaging, Windows process or migration guard was weakened.

## Current quality/error state

- Develop after this commit requires exact-current focused/canonical verification before any Beta or promotion-ready claim.
- UI and Backend exact-head canonical runs remain in progress and were not consumed prematurely.
- Historical Windows/runtime signatures remain release guards and are not reopened without exact-current reproduction.

## Tracker / visual state

- The 11-screen manifest and Visual-Gap ledger remain authoritative; no UI mutation or new pixel-match claim was made this run.
- `docs/development/ALPHA_BETA_PROGRESS.md` remains evidence source; no percentage was invented and no unverified capability was promoted.

## Next integration order

1. Re-check exact-current Develop CI before any further Develop mutation.
2. Consume final exact UI Quality `34304620632`; integrate its bounded navigation successor only if the exact head finishes green without superseding commits.
3. Consume final exact Backend Quality `34303936995` conservatively; prioritize dependency-unblocking Storage/WAL/schema work only after exact-green evidence.
4. Otherwise consume exactly one new bounded Core/UI successor with non-superseded exact evidence.
5. Preserve the Windows/Packaging/Runtime regression matrix before any Beta/release claim.

## Persistent release guards

Retain explicit Beta/release acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting including configured-upper-bound, one-token-with-margin, one-token-with-zero-margin and requested-vs-effective provenance; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no new Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
