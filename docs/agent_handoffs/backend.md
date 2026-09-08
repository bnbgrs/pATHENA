# pATHENA Backend & Systems Handoff

## Baseline

- Exact shared baseline reviewed: `develop/pathena-next@e6ed6eba803e4084b5e5aeaa2ad576dccdaf9961`.
- Pre-run Backend worker: `postmerge/backend@75e45f99ce60b87e0b56ea024d3bed931ec461d4`.
- History-preserving NON-FORCE sync: `ce2dd1d08302756b0932287a214177a0418d9132`, parents `75e45f99ce60b87e0b56ea024d3bed931ec461d4` and exact Develop `e6ed6eba803e4084b5e5aeaa2ad576dccdaf9961`. Develop-owned Integrator/startup-experience blobs were imported byte-identically; Backend v41/WAL lineage was preserved.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Handoffs consumed

- Error handoff and exact predecessor Quality were reviewed before mutation. Quality `34251875708` on `75e45f99ce60b87e0b56ea024d3bed931ec461d4` completed FAILURE: specification-validator, mypy, Linux-storage, Windows-path-safety and Local-install passed; Ruff and canonical pytest failed.
- Spec/Core handoff: §75 remains blocked on exact-green Backend v41 evidence.
- UI handoff reviewed; no UI product file authored.
- Integrator handoff on exact Develop reviewed before synchronization.

## ExternalAccessGateway priority

Exact Develop still contains the requested fail-before-side-effect runtime boundaries and regressions: `ttl_seconds` and `max_bytes` require genuine non-bool ints; `timeout_seconds` is numeric, non-bool and finite, rejecting NaN/Inf while preserving valid ranges. The prepared patch was not duplicated.

## Progress this run — exact Ruff import recovery

The prior v41 facade repair remains present. Exact current `schema.py` inspection showed the consolidated `schema_contract` import still placed `DatabaseCompatibilityError` after all uppercase constants rather than in Ruff/isort case-insensitive alphabetical order. Commits `86d1577160e0bdc843faa3ebc55964bfa2da0196` and corrective descendant `01eccfe3b688115f85345e365078cb11c193b749` move only that import; compare against sync commit `ce2dd1d08302756b0932287a214177a0418d9132` is exactly one addition and one deletion in `src/athena/storage/schema.py`. A transient accidental error-message edit in the first contents-API replacement was immediately restored in the descendant before handoff, so the net product diff is import-order-only.

Canonical Quality `34258124033` on exact product SHA `01eccfe3b688115f85345e365078cb11c193b749` is pending. No Ruff PASS, pytest PASS, global-green or promotion-ready claim is made before exact completion.

## Invariants retained

- v40→v41 remains additive, verified and transactional; Delta lower-bound provenance remains explicit and restart-durable.
- production migration does not silently tolerate malformed legacy fixtures.
- production WAL exact-type fail-closed guards remain unchanged.
- no silent Tor→Direct fallback; Direct fallback explicit only; no loopback/private proxy leak; redirect re-authorization preserved; HTTPS/default-port/compression/response-size boundaries fail closed.
- Audit/Provenance/fsync/transactional Source finalization unchanged.
- PASSIVE-only automatic WAL maintenance; explicit-idle TRUNCATE only; no manual WAL deletion.
- no new scheduler process/loop/thread/timer/retry, cryptography, lane-lock, process-tree, packaging or DirectChat changes.
- release crash-signature matrix retained without reopening absent exact-current reproduction.
- no force push, rebase, history rewrite or main mutation.

## Next Backend action

Consume exact Quality `34258124033`. If Ruff clears, mark only ERR-0026 fixed-pending-integrator verification. Then repair only exact assertion-level v41 fixture/current-schema drift without weakening production migration guards, followed by WAL test-collaborator drift using canonical concrete collaborators rather than loosening exact-type production boundaries. Run focused v40→v41/restart/Research/WAL plus ExternalAccessGateway/network-security regressions and canonical Quality. Do not hand §75 to Core/Integrator until Backend-owned exact failures are green.
