# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@a783e8d0f45f5beb888b8bd708d52124a44c3420`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization with current Develop: merge commit `6eb421cf5efc510898006868bfc475c7928bc32b`.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Current backend slice — capture URL runtime type boundary

Area: `ExternalAccessGateway.capture_url()` fail-before-side-effect runtime validation.

Product/test commit `07782c78d6e2cb1e9f4bfb6bf9175c9fb041a806` rejects non-text `url` values with `ExternalDestinationError("External URL must be text.")` before authorization/audit/actor/transport/Source paths. Valid text URLs retain the existing authorization, redirect re-authorization, transport, response-policy, fsync and transactional Source/audit/provenance flow.

The earlier exact-product Quality run `33818120429` completed `cancelled` with zero jobs, so it is explicitly not PASS evidence.

After the NON-FORCE sync, canonical Quality run `33822032100` was created on exact synchronized worker SHA `6eb421cf5efc510898006868bfc475c7928bc32b`. It currently has four real jobs running: Linux storage regressions, Python 3.12 quality, Local install smoke and Windows path safety. No PASS is claimed until completion.

## Retained invariants

- no silent Tor to Direct fallback;
- Direct fallback remains explicitly authorized only;
- loopback/private destination and proxy-leak protections unchanged;
- every redirect is re-authorized before fetch;
- HTTPS/default-port policy remains fail-closed;
- compressed-response and response-size policies unchanged;
- audit/provenance/fsync/transactional Source-finalization semantics unchanged;
- no retry, cryptography, storage, recovery or platform-path behavior changed.

## Next backend slice — reproduced External Research URL-container boundary

`ExternalResearchService.enqueue(urls=...)` currently computes:

`tuple(item.strip() for item in urls if item.strip())`.

This is a real runtime-boundary gap: a naked string is iterated character-by-character and non-text elements call `.strip()` incidentally, while bytes can flow as byte elements. The next bounded mutation should reject `str`/`bytes` as the URL container, require a real `Sequence`, require every element to be `str`, normalize/trim only after those checks, and fail before any `gateway.capture_url()` side effect. Valid sequence-of-text behavior and Gateway authorization/audit semantics must remain unchanged.

Do not implement or claim this next slice until the currently running exact synchronized Quality is consumed; if that run is red, classify and correct the exact failure first.

## Integrator handoff

Do not integrate `07782c78d6e2cb1e9f4bfb6bf9175c9fb041a806` yet. Wait for canonical Quality `33822032100` on synchronized worker SHA `6eb421cf5efc510898006868bfc475c7928bc32b` to complete. If green, independently review only the bounded Gateway product/test delta; temporary tooling history remains excluded.
