# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `c775d37f50e332639007ba162b4ff7f591434f1c`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `bfefb4fcd9f87e4587984e96689009366be77361`; spec-core `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00`; backend `5fb145df421059314b4d90f53b9fc69b1c4333ab`; UI `4c656c2c5dfb55e6d3f0078719183cbbad73a555`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, rebase, history rewrite, auto-merge or main promotion was used.

## Progress this run — UI-GAP-0074

UI-GAP-0074 was independently reviewed and integrated as the single bounded progress slice.

- Product commit: `ee2dafc9453c8e3b5d67aed107a955b086111f68`.
- Focused regression: `10ddf88043757628906480541e179323f5af7247`.
- Exact verified UI descendant: `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8`, canonical Quality `34187727628 = success`.
- Develop integration commit: `d06a1ef660c32df1315661f8b03648f0f8b807f5`.
- Independent Develop compare is ahead-only by one commit and exactly two files: `src/athena/desktop/jobs_workspace.py` (+10/-5) and `tests/unit/test_pathena_jobs_status_copy.py` (+44).

The visible nonzero-exit path no longer emits `Jobs command ... failed`. Refresh failures report `Jobs could not be refreshed`; show failures report that job details could not be loaded; action failures retain the exact operation, job label, background ownership and exit code. Process spawning, QProcess classification, receipt parsing, lifecycle state, scheduler/worker behavior, persistence, Security, Storage, Recovery and Windows runtime behavior are unchanged.

## Verification state

- Worker focused regression and canonical Quality are exact-green on the unchanged UI-GAP-0074 product/test lineage.
- Develop received the exact product blob from the product commit and exact focused-test blob from its direct test successor; divergent UI history was not imported.
- No exact-current-Develop canonical workflow is yet associated with `d06a1ef660c32df1315661f8b03648f0f8b807f5`; global-green/promotion-ready is not claimed.
- No Skip/XFail, assertion weakening or guard relaxation was introduced.

## Other worker state

- UI-GAP-0075 is also exact-green on UI descendant `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8` but was deliberately deferred to preserve the one-bounded-slice rule.
- UI-GAP-0076 remains `IMPLEMENTED_PENDING_VERIFY`; do not integrate until exact canonical Quality succeeds.
- Spec/Core §72 repair `124bdd9d789230d33452cfbc2452b307d410316c` remains `FIXED_PENDING_EXACT_VERIFY`; original `34186455107` was full-pytest red.
- Backend canonical-scheduler wrapper guard `6ce79db5ed3a11cfc58a7bb92323ae5b98817da5` has no exact completed workflow in its current handoff; not READY.
- ERR-0023 remains fixed pending exact Develop verification. ERR-0024 tracks the §72 pytest-only failure.

## UI / Alpha-Beta state

- Eleven-screen status remains implemented pending visual review; no MATCH claim is made without original-reference evidence.
- `docs/development/ALPHA_BETA_PROGRESS.md` was read; no percentage is inferred. The large tracker was not destructively rewritten because the connector response is truncated and a complete safe replacement body was not available.

## Next integration order

1. Obtain exact-current-Develop focused Jobs regressions + Ruff and canonical Quality for the descendant carrying `d06a1ef660c32df1315661f8b03648f0f8b807f5`.
2. If compatibility remains unchanged, integrate UI-GAP-0075 as one bounded exact-green slice.
3. Consume repaired Spec/Core §72 only after exact-green evidence; keep ERR-0024 open until then.
4. Consume Backend scheduler wrapper guard only after exact canonical success.
5. Preserve the release crash-regression matrix before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
