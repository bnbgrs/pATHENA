# Independent Manual Release-Closure Handoff

Generated: 2026-09-11
Branch: `manual/independent-release-closure-20260911`
Base: `develop/pathena-next@17d06d258ec2f5841049227504034ef601cdcdf8`

## Ownership / collision rule

This work deliberately does **not** modify `main`, `develop/pathena-next`, `postmerge/errors`, `postmerge/spec-core`, `postmerge/backend`, or `postmerge/ui`. No Storage product code, Qt/UI product code, packaging product code, workflow, or release guard is changed. The branch contains only independent diagnostics/acceptance tooling and QA coverage. Active workers should selectively reuse/cherry-pick only the pieces they own after revalidating against their then-current base.

## Storage identity — Backend + Fehlerjäger handoff

Added `scripts/audit_storage_identity_contract.py` plus QA coverage.

On the branch base the audit is expected to reproduce three exact open identity boundaries:

- `BE-046_POSIX_FD_CLOSED_BEFORE_PATH_UNLINK`: `_unlink_reserve_posix` validates through the open FD, closes it, then performs destructive unlink through `record.path`.
- `BE-046_NONPOSIX_PATHNAME_UNLINK_AFTER_IDENTITY_CHECK`: `_unlink_reserve_non_posix` captures pathname identity, then separately deletes by pathname.
- `BE-052_PREFLIGHT_IDENTITY_NOT_BOUND_TO_WRITER_OPEN`: `SQLiteDatabase.start()` performs `inspect_database_read_only(self.path)` and later separately calls `sqlite3.connect(...)`.

The audit exits `2` while those known product gaps remain and `0` when none of its signatures remain. It is diagnostic evidence, **not** the BE-046/BE-052 product fix. Backend remains owner of the actual identity-preserving primitive and adversarial native-Windows/POSIX acceptance tests. Error bot can use the stable finding names for deduplication.

## 11-screen UI evidence — UI bot handoff

Added `scripts/validate_ui_reference_evidence.py` plus QA coverage.

The validator enforces:

- exactly slots 01–11, exactly once and in canonical order;
- malformed rows fail closed;
- a `MATCH` claim is rejected if the original reference is not `AVAILABLE_OPENED`;
- a `MATCH` claim is rejected while the reference is `VISUAL_REFERENCE_PENDING`;
- machine-readable counts for opened references, pending references and MATCH claims.

On the branch base the manifest is structurally valid but still reports zero MATCH claims. This validator does not claim visual parity and does not replace opening the real reference/runtime image pair. UI worker remains owner of Qt product changes and same-state visual comparison.

## Windows / packaging / runtime — Integrator/Backend handoff

Added `scripts/validate_windows_release_contract.py` plus QA coverage.

The validator checks the repository-level release contract for:

- a `windows-latest` canonical lane;
- packaged app dispatch/process/Windows packaging contract regressions in that lane;
- Windows Core/API restart smoke;
- packaging metadata smoke;
- two-EXE desktop/worker contract assertions;
- packaged worker artifact contract;
- pypdf collection contract;
- locked `pypdf` runtime dependency;
- locked PySide6 desktop runtime dependency.

This is a static release-contract gate, not evidence that a freshly built Windows EXE launches successfully. The final release still needs exact-SHA Windows build/runtime/packaging evidence.

## QA file

`tests/qa/test_manual_release_closure.py` executes all three validators against the exact branch tree. The Storage assertion is intentionally a diagnostic canary for the current base: once Backend closes BE-046/BE-052, that assertion must be updated/removed rather than preserving the vulnerability signature.

## Commits

- `66c9537686c140005dcae953a8ad7aa7a410fb7f` — Storage identity-boundary audit.
- `f8b94982e0ac6810850429fd7782e1af2a168dcb` — fail-closed 11-screen evidence validator.
- `53d191782d8a3201b0f7e93030aa2add1a24025e` + `0a1f18f4b848a8a6fbea0c5002a8f87da0adcfa7` — Windows release-contract validator and token hardening.
- `890399c3440711985bb9889ae40d752a1d1f66b4` — QA execution of all three validators.

## Integration guidance

Do not merge this branch wholesale merely because CI is green. Treat it as independent evidence/tooling. Backend/Error should consume the Storage detector or its stable finding names; UI should consume the manifest validator; Integrator/Backend can consume the Windows release-contract validator. Rebase/revalidate each selected slice against the current Develop/worker head before integration.
