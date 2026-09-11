# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@95b636c982a800d75f7d219162a04f6c87976e9f`.
- Error worker entered this run at `postmerge/errors@6cbe3505896fa7bcc1155491862cce09813a42ed`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `103feb7ca6b3513077ce47f83569c13cc626b600`.
- Latest exact-current canonical Quality: `34560421777@95b636c982a800d75f7d219162a04f6c87976e9f = IN_PROGRESS`; no new failure is inferred while it is running.
- `postmerge/errors@6cbe3505896fa7bcc1155491862cce09813a42ed` had zero canonical Quality runs before the ledger mutation; after ledger commit `3494c8ab870d44a1b7d4017cc14a886328f05a95` there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 Windows proof gap identified on exact-current Develop

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

Current Develop `95b636c982a800d75f7d219162a04f6c87976e9f` is UI-owned (`fix(ui): make startup event filter teardown-safe`) and does not modify EmergencyReserve storage behavior. The BE-046 source-trace gap therefore remains current rather than historical.

The new evidence is in the focused regression surface itself. `tests/unit/test_emergency_reserve.py` has two adversarial parent-directory replacement tests, but both are POSIX-only:

- `test_posix_store_creation_does_not_publish_into_replaced_reserve_root`
- `test_posix_store_release_does_not_unlink_replacement_root_file`

Each explicitly skips when `os.name != "posix"`. The module contains no corresponding native-Windows reserve-parent substitution test. Therefore canonical Windows storage coverage can be green without exercising the adversarial condition needed to prove BE-046 closed.

This converts the prior broad request for a Windows proof into a concrete missing test contract: Backend must add native-Windows adversarial coverage for the non-POSIX create-success, failure-cleanup and release seams, and the implementation must fail closed without deleting or fsyncing through a substituted parent. A pathname-only recheck is not sufficient to establish handle-bound directory continuity.

No Backend product mutation was made on `postmerge/errors`; BE-046 remains explicitly owned by Backend and its current handoff contains no tested bounded product candidate. No Skip/XFail or invariant weakening was introduced.

### ERR-0035 — SQLite preflight identity is not carried into live writer startup

Status remains `OPEN`, P1, Backend / BE-052 owned. It remains distinct from ERR-0033 and is not selected ahead of BE-046 while Backend itself still ranks BE-046 first. No parallel product mutation was made.

### Closed clusters

`ERR-0036` remains `FIXED` via canonical `34544225707@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c = SUCCESS`.

`ERR-0034` remains `FIXED` via canonical `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`.

## Integrator handoff

- Current Develop: `95b636c982a800d75f7d219162a04f6c87976e9f`.
- Current canonical Quality: `34560421777 = IN_PROGRESS`; consume it before classifying any new Develop failure.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned. New exact-current evidence shows the existing adversarial parent-swap regression coverage is POSIX-only and is skipped on Windows, so a green Windows lane does not yet prove this root cause closed.
- Required BE-046 focused proof: native-Windows parent substitution at create-success, failure-cleanup and release, with fail-closed behavior and no mutation/durability operation through the substituted parent.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- No closed/stale cluster was reopened without exact-current reproduction.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.