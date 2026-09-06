# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `70f985ce7a28044824bfbfa53769b982fa152747`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `43c92a3a95ddcc124a0ec1ad081b5c102dd36f98`; spec-core `2e0a840d370c5aa076f660caabb78ba166253e39`; backend `33be60ac2c7a6ddda234c8166846e233e94c4053`; ui `c249c0ec1c3a3a19617bcb5c6f3c2d4899d4a0fd`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, history rewrite or auto-merge was used.

## Integrated this run — UI-GAP-0040 System detail keyboard focus

The UI handoff marks UI-GAP-0040 `FIXED / INTEGRATOR_READY`. Product commit `330fd20ec285b44dee8c9f89597a9c75e55c9c95` adds only `QLabel#systemDetail:focus` to the established canonical accent-border focus selector block. Focused regression `4cba0e0235ea5094f9f39b4d3f615879ca4362df` locks the selector and canonical accent token. Exact verified UI head `0d5a89b879ee0959a42734181adb129f4c3de024` passed Quality `34034051224 = success`.

The UI worker product parent also contained later/unconsumed selector context, so no worker history or whole worker blob was imported. The exact bounded semantic delta was applied directly to current Develop, together with the exact focused regression, in integration commit `97a8cc71bbc52dcf2cbba83a330d634ac36197d9`.

## Validation and error state

- UI source lineage canonical Quality `34034051224 = success`.
- Focused UI-GAP-0040 regression is included in that exact green lineage.
- Independent review confirmed the product delta is one selector and the regression is one nine-line test file.
- Exact-current-Develop global Quality is not yet claimed.
- No OPEN current exact-SHA error was established by this bounded UI slice; historical Windows runtime/crash classes remain release-acceptance guards only unless reproduced on the exact current SHA.

## UI state

- UI-GAP-0040 is integrated on Develop.
- Current UI handoff marks UI-GAP-0041 `IMPLEMENTED_PENDING_VERIFY`; it remains excluded until exact canonical Quality succeeds.
- All eleven screens remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no pixel-level `MATCH` claim is valid while original reference images remain pending.

## Alpha/Beta progress

`docs/development/ALPHA_BETA_PROGRESS.md` remains the canonical tracker. Complete connector retrieval has previously been truncated, so this run does not replace the whole file and risk data loss. UI-GAP-0040 integration evidence is versioned here pending safe tracker reconciliation.

## Next integration order

1. Prefer a newer bounded exact-green Core successor if compatible with current Develop.
2. Otherwise consume exactly one READY Backend/UI successor; UI-GAP-0041 remains excluded until canonical green evidence exists.
3. Obtain exact-current-Develop canonical Quality before any promotion/readiness claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata, fail-closed frozen argv routing and Desktop/Worker two-EXE split, exactly one Desktop with bounded/non-growing workers, adaptive 2048-context DirectChat budgeting, the Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError` crash cluster, and storage-bootstrap/migration startup signatures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
