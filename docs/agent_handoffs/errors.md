# pATHENA Error Handoff

## Baseline

- Develop: `09d43c348420dc5ad0eb2be80ebf8681ae8f25c5`; bounded paired-sidecar guard integrated; canonical Quality `34753048193 = IN_PROGRESS`.
- Error worker current harness lineage: `ef1e9d4cb40f1c17d8c28439312fdcdeb15baa4e` before final docs updates; exact workflow count = 0.
- Spec/Core: `e361ef5f365d7afd1d1b5d4b9fa242aeebfdee38`; Core Focused `34751831134 = FAILURE`; canonical `34751831135 = FAILURE`.
- Backend: `aab04d0c4564a07f9af5c12e6fa496a5e1038ff7`; owner-side Storage Focused/canonical exact-green; bounded Storage slice now integrated into Develop.
- UI: `3dfd310c06f3a6b3e34db0d524bf752269fe8bcc`; last exact UI Focused/Core Focused/canonical all green.
- `main` and `bnbgrs/ATHENA` remain untouched.

## Current error state

- OPEN: `ERR-0055`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0049`, `ERR-0053`, `ERR-0056`.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`, `ERR-0052`.
- STALE: prior stale IDs plus `ERR-0054`.
- BLOCKED: none.

## ERR-0049 — FIXED_PENDING_VERIFY / P1

The bounded two-file Storage fix from the exact-green Backend lineage is integrated into Develop at `09d43c348420dc5ad0eb2be80ebf8681ae8f25c5`.

Canonical Quality `34753048193` is already running for that exact SHA. Current job evidence: Linux Storage regressions = `SUCCESS`; Windows path safety/release guards = `SUCCESS`; Local Install + pypdf packaging = `SUCCESS`; Specification Validator = `SUCCESS`; Ruff = `SUCCESS`; mypy = `SUCCESS`; full pytest remains `IN_PROGRESS`.

Do not start a competing run and do not mutate Develop while it is active. Promote `ERR-0049` to `FIXED` only if that exact canonical completes `SUCCESS`. If it fails, classify the exact new signature before attributing it to Storage.

## ERR-0055 — OPEN / P2

Current Spec/Core SHA `e361ef5f365d7afd1d1b5d4b9fa242aeebfdee38` has a single exact lint blocker: Ruff `I001` in `tests/unit/test_user_correction_policy.py:1:1`.

Core Focused `34751831134` and canonical `34751831135` are both red. Diagnostics show one behavior-neutral Ruff remediation: remove the extra blank line immediately before `USER_ID`. Canonical full pytest, Linux Storage, Windows path/release guards and Local Install all pass on the same SHA.

Ownership remains Spec/Core. Error worker does not edit the worker-owned policy/test in parallel. Consume the next exact Spec/Core successor; require both Core Focused and canonical `SUCCESS` before owner-side closure.

## ERR-0056 — FIXED_PENDING_VERIFY / P2 harness

The same exact Core-Focused diagnostics exposed an independent harness gap: `tests/unit/test_user_correction_policy.py` was changed but the workflow reported `No changed Core-owned unit-test files selected; lint evidence only`.

Root cause: `.github/workflows/core-focused-candidate.yml` omitted `tests/unit/test_user_correction*.py` from the pull-request path trigger and omitted `test_user_correction.*` from its focused-test selector.

Error-owned fix on `postmerge/errors`:

- `4b723fe7202c841e0c768aaf3a62600eaadf02ff` adds both selector entries.
- `ef1e9d4cb40f1c17d8c28439312fdcdeb15baa4e` adds `tests/unit/test_core_focused_candidate_workflow.py` to guard those contracts.

This expands mandatory test coverage; it does not weaken or skip anything. The exact Error-worker SHA has no workflow run, so no CI PASS is claimed. Integrate/exercise this bounded harness slice and require exact evidence that a changed user-correction test is selected and passes before `FIXED`.

## ERR-0053 — FIXED_PENDING_VERIFY / P2

UI successor `3dfd310c06f3a6b3e34db0d524bf752269fe8bcc` remains owner-side exact green in current consumed evidence. No current deterministic UI failure is reproduced.

The bounded historical product fix is `541c367547c698489ad548cc791f72dd27d141b4`, changing only `src/athena/desktop/pathena_shared_components.py` to derive the rendered send-button geometry from `SHELL.composer_action_size`. Current UI and Develop have since diverged with many unrelated UI/evidence changes, so the whole current UI branch must not be promoted for `ERR-0053`. Extract only the bounded verified geometry slice plus relevant tests, then require exact Develop canonical success.

## ERR-0054 — STALE

The historical visual-baseline failure remains non-authoritative because it was last reproduced on superseded UI SHA `541c367...`. Reopen only from a current exact-SHA visual failure. Do not weaken visual gates or accept generated baselines blindly.

## Source-of-truth note

Backend/UI handoff files contain older baseline narratives and are not authoritative over current branch heads/runs. Current exact SHAs and run outcomes above take precedence; historical handoff content is retained only as ownership/context evidence.

## CI discipline

- No competing canonical run was started.
- No Backend/UI/Spec-Core product branch was mutated by Error worker.
- Error worker only changed its own docs plus Error-owned Core-Focused workflow/test harness.
- `main` and `bnbgrs/ATHENA` stayed read-only.
- No force push, history rewrite, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation occurred.

## NEXT_ROOT_CAUSE

1. Consume Develop canonical `34753048193` on `09d43c348...`; `SUCCESS` closes `ERR-0049`, while any failure must be classified from exact evidence.
2. Consume the next Spec/Core successor for `ERR-0055`; expected bounded fix is Ruff-only and behavior-neutral.
3. Qualify/integrate Error-owned `ERR-0056` harness coverage so user-correction tests cannot silently fall out of Core Focused.
4. Keep `ERR-0053` pending integrated Develop verification; extract only its bounded historical geometry slice, not the full current UI branch.
5. Do not reopen `ERR-0054` without a current exact visual reproduction.
