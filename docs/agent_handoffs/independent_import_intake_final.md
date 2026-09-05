# Independent Import Intake Final Handoff

## Status

`IMPLEMENTED_PENDING_VERIFY`

## Ownership

Independent assistant-owned slice. Active workers should not duplicate or edit these paths while this branch is under canonical verification:

- `src/athena/source/import_intake.py`
- `tests/unit/test_import_intake.py`
- `docs/agent_handoffs/independent_import_intake_final.md`

No shared Backend, Research/Core, UI, Error-ledger, schema, job-service, or application-composition file is modified by this slice.

## Branch and baseline

- branch: `independent/import-intake-final-20260905`
- exact original base: `develop/pathena-next@f90160f4a4269394215927bec07ac047b6297d1e`
- previous experimental branch `independent/import-intake-20260904` is superseded for integration purposes and must not be merged.

## Specification boundary

Primary anchor: `docs/beta/04_Quellen_Roharchiv_und_Import-Pipeline.md`, especially §§7–18.

This bounded vertical slice implements the intake layer immediately above the existing canonical `SourceCaptureService`:

- exact JSON-persistable `ImportRequest` contract;
- file, multi-file and folder roots;
- recursive/non-recursive deterministic discovery;
- explicit origin metadata;
- optional protection-scope forwarding;
- default no-follow symlink/junction policy;
- optional follow-inside-selected-root with outside-boundary rejection and directory-cycle detection;
- obvious system/metadata filtering with explicit non-semantic reporting;
- max-file-size and expected-count preflight;
- local spool free-space preflight;
- Archive Root availability warning while preserving local-spool behavior;
- `temporary` and `do_not_store` fail closed in this durable Raw Archive slice instead of silently persisting contrary to policy;
- controlled one-time retry when `SourceChangedDuringCaptureError` reports source mutation;
- import-level `READY`, `PARTIAL`, `FAILED` result;
- sanitized capture failures retaining exception type only.

Actual physical staging, streaming SHA-256, Blob verification/deduplication, protected encryption and authoritative Source persistence remain owned by the already-existing `SourceCaptureService` / Blob stores and are deliberately not duplicated here.

## Explicit non-goals

The following are separate later slices and must not be inferred as completed by this handoff:

- OCR/STT providers;
- archive/container expansion;
- MIME/magic-byte format profiling;
- representation scheduling;
- semantic extraction / Knowledge / Memory writes;
- UI/API wiring;
- durable Jobs orchestration around the JSON-safe request;
- changes to `main`.

## Tests

`tests/unit/test_import_intake.py` covers:

1. exact durable JSON round-trip;
2. bool-safe scalar validation;
3. canonical absolute path validation;
4. deterministic recursive enumeration;
5. recursive=false behavior;
6. default no-follow symlink behavior;
7. follow-policy outside-root rejection;
8. directory-cycle detection;
9. max-file-size and expected-count preflight;
10. fail-before-capture `temporary` and `do_not_store` semantics;
11. offline Archive Root warning semantics;
12. exactly-one mutation retry;
13. sanitized second-attempt failure with no unbounded retry;
14. partial capture state;
15. exact protected-scope forwarding.

## Collision review at start

Current worker diffs against `develop/pathena-next@f90160f4...` were inspected before implementation:

- `postmerge/backend`: Storage Health product/tests + backend handoff only.
- `postmerge/spec-core`: Research repository + Core handoff only.
- `postmerge/ui`: Settings runtime/UI ledgers/tests only.
- `postmerge/errors`: Error handoff/ledger only.

No active worker touched or claimed the import-intake paths.

## Integration rule

Do not auto-merge while status is `IMPLEMENTED_PENDING_VERIFY`.

Before integration:

1. canonical ATHENA Quality Gate must pass on the exact final branch head;
2. refresh Develop head and compare for new collisions;
3. if no import-intake path collision exists, consume only the exact green product/test/handoff content;
4. record the exact Quality run ID and final SHA here;
5. only then promote status to `VERIFIED`.
