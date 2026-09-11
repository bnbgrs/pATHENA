# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@95b636c982a800d75f7d219162a04f6c87976e9f`.
- Error worker entered this run at `postmerge/errors@01f1ff53321f89c21aef06be32f1ce3ad9826e82`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `c51ef04787ef6affa2e6acc3a902e138cf6b7409`.
- Latest exact-current canonical Quality: `34560421777@95b636c982a800d75f7d219162a04f6c87976e9f = SUCCESS`.
- `postmerge/errors@01f1ff53321f89c21aef06be32f1ce3ad9826e82` had zero canonical Quality runs before the ledger mutation; after ledger commit `0fe9d684c2b366f900f002b6d3af35272953d694` there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0037 closed with exact failure and exact repair evidence

### ERR-0037 — startup event filter teardown/partial-init lifecycle race

Status: `FIXED`, P1 when it blocked canonical Develop.

The immediately previous Develop SHA `b1e77f8a4b90c12fe75e257b96303cc137d760a9` failed canonical Quality `34556269271`. Windows path safety, Linux storage and Local-install were green; Python quality failed only at pytest.

The canonical diagnostics artifact records exactly `1 failed, 4830 passed, 3 skipped`. The sole failing test was `tests/unit/test_pathena_transient_dialog_shortcuts.py::test_tab_and_backtab_stay_inside_transient_surfaces`, with `AttributeError` from `PathenaStartupExperience.eventFilter()` because `self.chat_messages` did not yet exist during a Qt lifecycle callback.

The root cause is therefore bounded to event-filter lifecycle safety: the filter directly dereferenced an attribute that Qt may access while the Python wrapper is partially initialized or being torn down.

The adjacent current Develop commit `95b636c982a800d75f7d219162a04f6c87976e9f` changes only `src/athena/desktop/pathena_startup_experience_2900.py`, replacing the direct dereference with `chat_messages = getattr(self, "chat_messages", None)` and checking the object only when present. No test or guard was loosened.

Closure is exact: canonical Quality `34560421777@95b636c982a800d75f7d219162a04f6c87976e9f = SUCCESS`. The pytest job and all Windows path-safety/storage/durable-fs/runtime/ownership/packaging/chat-reserve, Linux-storage and Local-install lanes completed successfully.

No Error-branch product mutation was required because the bounded repair was already integrated on current Develop and exact-SHA canonical green.

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

Current source still leaves the non-POSIX parent-directory identity unbound across create-success, failure-cleanup and release. Existing adversarial parent-replacement tests are POSIX-only. Backend still owns the product root cause and has no tested bounded candidate in its current handoff, so Errors does not parallel-mutate Storage code.

Required proof remains native-Windows adversarial parent substitution across create-success, failure-cleanup and release, with fail-closed behavior and no delete/durability action through a substituted parent.

### ERR-0035 — SQLite preflight identity is not carried into live writer startup

Status remains `OPEN`, P1, Backend / BE-052 owned. It remains distinct from ERR-0033 and has no current tested Backend candidate. No parallel product mutation was made.

## Integrator handoff

- Current Develop: `95b636c982a800d75f7d219162a04f6c87976e9f`.
- Current canonical Quality: `34560421777 = SUCCESS`.
- `ERR-0037 = FIXED`: exact red predecessor `b1e77f8a…` / run `34556269271`; exact repair `95b636c…`; exact green closure `34560421777`.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned; native-Windows parent-identity closure evidence is still missing.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- No closed/stale cluster was reopened without exact-current reproduction.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
