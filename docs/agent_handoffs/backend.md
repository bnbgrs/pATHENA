# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@d1ca4580b129f5b255215ce415f4e627b22dbc63`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `1ca844d7f5d8a90165e3b109fe1a7caa1880d877`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- History-preserving NON-FORCE synchronization: `6feb9f8a5e6d246f7aba19e4932342988a2c2b7b`, with parents prior Backend head `1ca844d7f5d8a90165e3b109fe1a7caa1880d877` and exact Develop `d1ca4580b129f5b255215ce415f4e627b22dbc63`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage remain present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health unavailable-path invariant — VERIFIED

Product `3421ea19c33b16a7694d7cb96951787225cb0d4c` requires a concrete database path for the unavailable state. Focused test `fbc3e214b822e8f25477ece0248d21f5fbe5d4fe` verifies fail-closed rejection of an unavailable snapshot without a path. Exact Backend descendant `1ca844d7f5d8a90165e3b109fe1a7caa1880d877` passed canonical ATHENA Quality `33955258771 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health NUL-path invariant — PRODUCT_FIXED / TESTS_ADDED_PENDING_VERIFY

`StorageHealthSnapshot` previously accepted `database_path` strings containing NUL characters. Such values can appear non-empty and non-whitespace while not representing a usable filesystem identity on supported Windows/Linux runtime paths.

Product commit `8db21b28775278f245f2b8387e51c2584b7147fd` now rejects non-None `database_path` values containing `\x00` before state-specific acceptance. Existing valid paths and all storage state semantics remain unchanged.

Focused test commit `6aadebad0e14fd29a74237fcec82142bb60785ab` covers both an all-NUL path and an embedded-NUL path and requires rejection before any downstream use.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until an exact product-containing descendant canonical Quality run is green.

## Invariants retained

- storage telemetry remains read-only and does not mutate SQLite/WAL state;
- no persistence format, transaction, recovery, fsync or Source finalization semantics changed;
- valid Windows/Linux storage paths remain unchanged;
- local model transport remains loopback-only, proxy-free and redirect-rejecting;
- response-size and total-deadline enforcement remain fail-closed;
- no new retries, routing behavior or cryptography;
- no silent Tor -> Direct fallback; Direct remains explicit-only;
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy and compressed-response rejection unchanged;
- audit and provenance semantics unchanged;
- no Skip/XFail, assertion weakening or guard relaxation;
- no merge to `main`, force-push or history rewrite.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: StorageHealth unavailable-path product `3421ea19c33b16a7694d7cb96951787225cb0d4c` + tests `fbc3e214b822e8f25477ece0248d21f5fbe5d4fe` through exact green Backend head `1ca844d7f5d8a90165e3b109fe1a7caa1880d877`, Quality `33955258771 = success`.
- NOT READY: StorageHealth NUL-path product `8db21b28775278f245f2b8387e51c2584b7147fd` + tests `6aadebad0e14fd29a74237fcec82142bb60785ab` until exact descendant canonical green evidence.

## Next backend slice

Consume the first exact canonical Quality run containing `6aadebad0e14fd29a74237fcec82142bb60785ab` or a documentation-only descendant. If green, mark StorageHealth NUL-path hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If no run binds, use an alternate executable verification path or take a disjoint real Backend/System slice rather than repeating the runner blocker. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
