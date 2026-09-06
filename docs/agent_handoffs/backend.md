# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@6c7fdb4f2cf22215ac065ce6d2fad7b15e54b650`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `87b73ef3f5448c58e1082d514c49067ff370f060`, parents prior Backend `22db94266d9219bdcf01a4567d0262f236f9fcad` + exact Develop `6c7fdb4f2cf22215ac065ce6d2fad7b15e54b650`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Verified predecessor

- Exact WAL checkpoint status-shape worker head `22db94266d9219bdcf01a4567d0262f236f9fcad` passed canonical ATHENA Quality Gate `34042444478 = success`.
- This exact-green lineage retains non-bool exact integer PRAGMA validation, non-negative WAL frame counters and exact three-field `wal_checkpoint(TRUNCATE)` status acceptance.
- ExternalAccessGateway runtime-boundary lineage remains previously verified exact-green; no current contradictory evidence reopens it.

## Current slice

Area: Storage / Recovery / migration journal-mode status shape.

Product `1e3a28402343628b2fdfd3cb53ae78bf3ac21801` requires `PRAGMA journal_mode = DELETE` to return exactly one status field before the candidate is accepted as having left WAL mode. Previously a malformed multi-field row could be accepted because only `mode[0]` was inspected and trailing runtime status data was ignored.

Focused regression `38d91a38c02e18d65f5e58234f1e72ea0948eafb` covers empty and two-field journal-mode rows plus the canonical single-field `("delete",)` row.

## Invariants

- candidate-only schema migration; live DB untouched;
- absolute regular non-link candidate and safe ancestry required;
- exact non-bool integer PRAGMA values retained;
- WAL checkpoint status remains exactly three fields;
- WAL frame counters remain non-negative;
- complete WAL checkpoint remains required;
- journal-mode status must be exactly one field and exact text `delete` case-insensitively;
- sidecar-free activation handoff retained;
- no Security/TOR/Provider/UI semantics, schema representation, WAL format, retries or cryptography changes.

## Verification

- Predecessor exact canonical Quality `34042444478 = success` on `22db94266d9219bdcf01a4567d0262f236f9fcad`.
- Current focused test head `38d91a38c02e18d65f5e58234f1e72ea0948eafb` has ATHENA Quality Gate `34045576145` pending at handoff-write time.
- No PASS or Integrator-ready claim is made for the new journal-mode-shape slice until an exact containing run completes successfully.

## Coordination

- Error handoff reviewed: OPEN=none, IN_PROGRESS=none, FIXED_PENDING_VERIFY=none; ERR-0016/ERR-0017 remain fixed.
- Current Spec/Core worker head reviewed: `4ebe23f510a0b36d8f87e027088de54a9809148a`; Core-owned Search/Memory work remains disjoint.
- Current UI worker head reviewed: `b021424a3d6b79786b695b00356c2f98fa7390dc`; UI-owned Settings focus work remains disjoint.
- Integrator/Develop head reviewed: `6c7fdb4f2cf22215ac065ce6d2fad7b15e54b650`.

## Integrator handoff

READY: exact WAL checkpoint status-shape lineage `22db94266d9219bdcf01a4567d0262f236f9fcad` / Quality `34042444478 = success`.

NOT READY: journal-mode exact-status-shape product `1e3a28402343628b2fdfd3cb53ae78bf3ac21801` + focused regression `38d91a38c02e18d65f5e58234f1e72ea0948eafb` pending exact canonical completion.

## Persistent release regression knowledge

Retain without reopening absent exact-current reproduction: Windows pypdf packaging metadata; fail-closed frozen child argv; two-EXE Desktop/Worker split; exactly one Desktop with bounded workers; adaptive small-context DirectChat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; duplicate `source_processing_job_id`; Core startup failure; storage-bootstrap startup failure.

## Next backend slice

Consume the first exact canonical Quality containing `38d91a38c02e18d65f5e58234f1e72ea0948eafb` or this documentation descendant. If green, promote only the journal-mode exact-status-shape slice and continue to the highest current unclaimed disjoint Backend/System gap. If red, repair only the smallest Backend-owned primary failure without weakening Storage/Recovery, ExternalAccessGateway, persistence, provenance or platform invariants. If cancelled, do not repeat unchanged; use another executable verification route or a distinct real Backend/System slice.
