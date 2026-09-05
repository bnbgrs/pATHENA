# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@c887b2beb4b0f919fdd4f86d3db245c16c2094f4`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `35e4858146ea7ad423da6ec5d59ce8d2e8eb4115`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- History-preserving NON-FORCE synchronization: `175903943b4e243811bf4bde02d05858b82deee0`, with parents prior Backend head `35e4858146ea7ad423da6ec5d59ce8d2e8eb4115` and exact Develop `c887b2beb4b0f919fdd4f86d3db245c16c2094f4`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage remain present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health unavailable-path invariant — VERIFIED

Product `3421ea19c33b16a7694d7cb96951787225cb0d4c` requires a concrete database path for the unavailable state. Focused test `fbc3e214b822e8f25477ece0248d21f5fbe5d4fe` verifies fail-closed rejection of an unavailable snapshot without a path. Exact Backend descendant `1ca844d7f5d8a90165e3b109fe1a7caa1880d877` passed canonical ATHENA Quality `33955258771 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health NUL-path invariant — VERIFIED

Product `8db21b28775278f245f2b8387e51c2584b7147fd` rejects NUL-containing `database_path` strings before state-specific acceptance. Focused tests `6aadebad0e14fd29a74237fcec82142bb60785ab` cover all-NUL and embedded-NUL paths. Exact Backend descendant `35e4858146ea7ad423da6ec5d59ce8d2e8eb4115` passed canonical ATHENA Quality `33958054144 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health NUL-detail invariant — PRODUCT_FIXED / TESTS_ADDED_PENDING_VERIFY

`StorageHealthSnapshot.detail` previously accepted strings containing NUL characters. Detail is runtime diagnostic text propagated into status/transport/presentation paths, so NUL-containing values are not a usable textual diagnostic boundary.

Product commit `60af3d61e687108fb07ed3569dd5459f4721b551` rejects non-None detail values containing `\x00` after existing non-empty/non-whitespace validation and before status-specific acceptance. Existing generated StorageHealthService diagnostics remain unchanged.

Focused test commit `8bb2adb2951900a0389eab57e1d4735b87cb0d29` covers all-NUL and embedded-NUL detail values and requires fail-closed rejection.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until an exact product-containing descendant canonical Quality run is green.

## Invariants retained

- storage telemetry remains read-only and does not mutate SQLite/WAL state;
- no persistence format, transaction, recovery, fsync or Source finalization semantics changed;
- valid Windows/Linux storage paths and valid diagnostic text remain unchanged;
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
- READY: StorageHealth NUL-path product `8db21b28775278f245f2b8387e51c2584b7147fd` + tests `6aadebad0e14fd29a74237fcec82142bb60785ab` through exact green Backend head `35e4858146ea7ad423da6ec5d59ce8d2e8eb4115`, Quality `33958054144 = success`.
- NOT READY: StorageHealth NUL-detail product `60af3d61e687108fb07ed3569dd5459f4721b551` + tests `8bb2adb2951900a0389eab57e1d4735b87cb0d29` until exact descendant canonical green evidence.

## Next backend slice

Consume the first exact canonical Quality run containing `8bb2adb2951900a0389eab57e1d4735b87cb0d29` or a documentation-only descendant. If green, mark StorageHealth NUL-detail hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If no run binds, use an alternate executable verification path or take a disjoint real Backend/System slice rather than repeating the runner blocker. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
