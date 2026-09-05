# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA observed this run: `4ce70615cffcbf0e76ec404e7e58b34c7c5e308a`
- Worker branch: `postmerge/errors`
- Error branch pre-run head: `eaa7e17d8425a05682e011639504d8266c32acb9`.
- History-preserving NON-FORCE synchronization with current Develop: `02ff9a758aaf15a9a66db44cf314a5f7839d6e91`; no force ref update, rebase or history rewrite.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0012`, `ERR-0013`.
- FIXED: `ERR-0001` through `ERR-0011`.
- BLOCKED: none.

## Fresh evidence

- UI correction Quality `33964058090@cef280487dd12b6fe88d4a3f021ec9b1b2aea0d5` completed `failure`.
- `ERR-0012` product correction is present and exercised successfully in that run: Windows path safety PASS, Linux storage PASS, local install smoke PASS, specification validator PASS, mypy PASS and full pytest PASS across 4660 collected tests. The former StorageHealth unavailable-path failure does not recur.
- The only canonical blocker is Ruff. Exact diagnostics artifact reports `I001 [*] Import block is un-sorted or un-formatted` at `tests/unit/test_pathena_settings_provider_detail_whitespace.py:11:1` on the PySide6/ATHENA import block.
- This is a new, deduplicated UI harness defect and is recorded as `ERR-0013`, not folded into StorageHealth `ERR-0012` and not treated as a recurrence of startup/readiness `ERR-0004`.
- Current UI head `77b3f9582d4530dbe081e3c81b8768ad00d3f050` is six commits ahead of `cef280487...` and removes the redundant unformatted provider-detail whitespace harness while retaining provider-detail state coverage and the corrected StorageHealth guard.
- Canonical replacement Quality `33966822035@77b3f9582d4530dbe081e3c81b8768ad00d3f050` is currently `in_progress`; no PASS/FIXED/READY claim is made for that head yet.
- Current Backend head observed: `1cc0017d560a1534de1fc2c83989d26e05238236`.
- Current Develop `4ce70615cffcbf0e76ec404e7e58b34c7c5e308a` has no exact-head repository-wide global-green claim here.

## Collision avoidance

- Do not mutate UI/Storage product or UI harness code from Error while the active UI worker already carries the corrections and an exact canonical verification is running.
- Do not weaken `test_storage_health_snapshot_requires_path_for_unavailable_state`; it correctly caught product-tree drift.
- Do not suppress Ruff I001 or remove non-redundant provider-state assertions to manufacture green.
- Preserve direct total-deadline, cumulative byte-budget, delegated body-handle/file-descriptor restrictions, loopback-only/proxy-free transport, Security, Storage and Recovery guards.
- No skip/XFail, assertion weakening, dummy success, force-push, history rewrite or merge to main.

## Integrator handoff

- `ERR-0001` through `ERR-0011` remain error-cleared on recorded exact evidence.
- `ERR-0012` remains `FIXED_PENDING_VERIFY`: its product invariant passes on `cef280487...`, but that exact Quality run is globally red for independent Ruff `ERR-0013`.
- New `ERR-0013` is `FIXED_PENDING_VERIFY`: exact Ruff I001 is known and current UI descendant `77b3f958...` removes the redundant offending harness, but replacement Quality is still running.
- Reject UI `cef280487dd12b6fe88d4a3f021ec9b1b2aea0d5` / Quality `33964058090` as READY despite pytest success because canonical Ruff is red.
- Do not declare current UI `77b3f9582d4530dbe081e3c81b8768ad00d3f050` READY or either pending error FIXED until exact canonical Quality `33966822035` completes successfully.
- Current Develop still requires exact-head canonical Quality before any repository-wide global-green claim.

## Next scan

1. Consume exact UI Quality `33966822035@77b3f9582d4530dbe081e3c81b8768ad00d3f050` when complete.
2. If successful, verify the StorageHealth unavailable-path guard remains present and Ruff I001 is absent, then close both `ERR-0012` and `ERR-0013` as `FIXED` with exact evidence.
3. If red, extract the new exact primary diagnostic, classify product vs harness, deduplicate, and allocate a new ID only for a genuinely distinct root cause.
4. Continue Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt/Desktop, Security, Windows path safety, Linux storage and local install/start scanning for real current-lineage failures.
