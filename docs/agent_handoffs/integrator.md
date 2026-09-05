# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `b5d888b09774e70a389457f568a8079faf130b5e`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `0017b4d83481ba46e020d12492eb5c1d0a5fca7a`; spec-core `38d83997e5fb183570f277385dbff85525ab99dc`; backend `8d07a57809507ada1ae5a87cd1fb6e360b66f74d`; ui `a0ba6bd47f4b8a6e91e8f6c222334c99cbe1a3aa`.
- `main` and `bnbgrs/ATHENA` were untouched.

## Integrated this run — truthful Local+Web candidate freeze

READY Core lineage independently reviewed:

- bounded product/test commit `31a52e034c154759a2ccce2eebc77a2f2d961f37`;
- exact canonical-green descendant `372697dbbb356ac0bbedfbd4d27f917c38fcefac`;
- focused execution `33992910995 = success`, 12 passed, Ruff PASS, mypy PASS;
- canonical Quality `33993014519 = success`.

Compatibility was checked at blob level before integration: current Develop `src/athena/research/repository.py` blob `1538b79220be19c1934cbc3028764c60185c47ea` exactly matched the product commit parent, and current Develop `tests/unit/test_research_local_plus_web.py` blob `f0d54a76ce1ed5b03ad1f875f2ccd7980f0e3726` also exactly matched the product commit parent. Only the verified product blob `20fb0286d02048b612aa4b1624a47530d4d3abc4` and acceptance-test blob `ab5b0e090010dbcf0a581b83b378883dd580efb0` were overlaid; temporary applicator workflow/script and older worker history were excluded.

Integration commit: `0d490e59e27a3289cc44dc4a366fd304c11b68cf`.

## Contract now covered

- `ResearchRepository.freeze_local_candidates()` accepts `LOCAL_PLUS_WEB` only with canonical persisted Internet scope;
- authorization UUID and captured Source IDs must be canonical and the durable authorization linkage must exactly match;
- local candidates remain pinned to the authoritative snapshot/time/type visibility rules;
- Sources carrying unrelated external-capture linkage are excluded from the local portion;
- only Sources linked to the exact current authorization may re-enter the Local+Web union;
- unrelated historical captures and post-snapshot Sources remain excluded;
- Local Exhaustive and Historical Backfill behavior remains unchanged;
- no transport call or synthetic Source/Claim/Evidence/Provenance/PALLAS data is introduced by freeze.

## Validation state

- Exact worker focused suite and canonical Quality are green as cited above.
- Exact-current-Develop repository-wide green is not claimed until a post-integration run exists.
- `ALPHA_BETA_PROGRESS.md` was read, but a complete safe rewrite was not attempted because connector retrieval is truncated for the large tracker; this handoff records the exact integrated evidence without fabricating tracker state.

## Runtime/release guards retained

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions. This Research slice does not modify their owning code or claim Windows promotion readiness.

## Other current inputs

- Backend has a newer canonical threshold-boundary handoff and must be independently reviewed before selection.
- UI has a newer workspace-action-focus candidate and must be exact-green before integration.
- `ERR-0014` remains STALE and reopens only on exact exit-139 recurrence.
- Eleven UI screens remain implemented pending visual review; pixel-level MATCH remains unclaimed.

## Next integration order

1. Inspect the remaining production Knowledge/Claims paths for any contradiction-review enqueue bypass, or consume another exact-green bounded Core successor if one appears.
2. Otherwise independently review exactly one READY Backend/UI successor.
3. Obtain exact-current-Develop Quality before any repository-wide green claim.
4. Before Beta/release readiness, explicitly regress known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes.

## Rules retained

- No direct work on `main`; no main promotion.
- No force-push, history rewrite or auto-merge.
- No Skip/XFail, weaker assertions, Security/Storage/Windows/Recovery/validator relaxation, fake success or fabricated provenance.
