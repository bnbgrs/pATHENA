# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next@6c7fdb4f2cf22215ac065ce6d2fad7b15e54b650`.
- Error branch history-preserving NON-FORCE synchronization: `db5c45e40e9b7ab7b9114d7f07f4dc69b5f1ce65`, parents prior Error head `df0009ddc998216638ff63d426310138b34ddd2c` + exact Develop `6c7fdb4f2cf22215ac065ce6d2fad7b15e54b650`.
- Worker heads reviewed: Backend `22db94266d9219bdcf01a4567d0262f236f9fcad`; Spec/Core `a47d4902c44d1a2126536cef65cb5f858aaa7fe9`; UI `b021424a3d6b79786b695b00356c2f98fa7390dc`; Integrator/Develop `6c7fdb4f2cf22215ac065ce6d2fad7b15e54b650`.
- `spec-core.md`, `backend.md`, `ui.md`, `integrator.md`, current worker heads and canonical Quality evidence were reviewed before mutation.
- `main` and `bnbgrs/ATHENA` remained strictly read-only; no force update, rebase or history rewrite was used.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Current canonical evidence

- Previously pending UI `postmerge/ui@81b8d6c2c250a412bb2947b2b356d9111c10b995` is now exact-canonical-green: Quality `34040342678 = success`. This closes the prior evidence wait; it does not create a new Error entry.
- Current Spec/Core `postmerge/spec-core@a47d4902c44d1a2126536cef65cb5f858aaa7fe9` is exact-canonical-green: Quality `34041882996 = success`; no error-owned primary failure is established.
- Current Backend `postmerge/backend@22db94266d9219bdcf01a4567d0262f236f9fcad`, Quality `34042444478`, is still in progress. Completed jobs are green: Windows path safety PASS, Linux storage + API runtime path-boundary PASS, local install/Core-API restart PASS, Validator PASS, Ruff PASS and mypy PASS; full pytest is still running. No failure evidence exists yet.
- Current UI `postmerge/ui@b021424a3d6b79786b695b00356c2f98fa7390dc`, Quality `34043271088`, is still in progress. Completed jobs are green: Windows path safety PASS, Linux storage + API runtime path-boundary PASS, local install/Core-API restart PASS, Validator PASS, Ruff PASS and mypy PASS; full pytest is still running. No failure evidence exists yet.
- Current Develop `6c7fdb4f2cf22215ac065ce6d2fad7b15e54b650` has no exact completed canonical Quality observed in this run and is therefore not promotion-ready by Error criteria.

## Verified closures retained

`ERR-0016` and `ERR-0017` remain FIXED on corrected-lineage canonical Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe = success`; no exact-current contradictory evidence reopens them. `ERR-0004` remains FIXED. `ERR-0014` remains STALE absent exact recurrence.

## Integrator handoff

- UI source head `81b8d6c2c250a412bb2947b2b356d9111c10b995` is now confirmed exact-canonical-green by `34040342678 = success`; its already integrated bounded UI-GAP-0042 lineage has no Error-ledger objection.
- Spec/Core head `a47d4902c44d1a2126536cef65cb5f858aaa7fe9` is exact-canonical-green by `34041882996 = success` and has no Error-ledger objection.
- Do not consume Backend `22db94266d9219bdcf01a4567d0262f236f9fcad` or UI `b021424a3d6b79786b695b00356c2f98fa7390dc` as exact-green until their current full pytest and workflows complete successfully.
- Do not reopen or reapply `ERR-0016` / `ERR-0017` absent exact-current contradictory evidence.
- Preserve Provider/Transport byte-budget/deadline/poisoning semantics, Personal-Memory provenance/review controls, Windows path safety, Storage, Security and Recovery guards.
- Current Develop still requires its own exact-SHA completed canonical evidence before promotion/readiness.

## Persistent Beta/release regression knowledge

Retain as explicit release acceptance without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume Backend Quality `34042444478` and UI Quality `34043271088` to completion.
2. Check the next exact current Develop/worker canonical or runtime signal.
3. Deduplicate against the ledger and persistent crash matrix.
4. On a concrete primary failure, finalize root cause and either perform the minimal Error-owned fix or concretely verify the responsible worker correction in the same run.