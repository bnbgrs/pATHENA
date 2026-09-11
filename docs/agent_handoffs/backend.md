# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline consumed first: `develop/pathena-next@b26eea46c89a8b628c2006d24d1fdac7492baa91`.
- Exact canonical Quality: `34601243038@b26eea46c89a8b628c2006d24d1fdac7492baa91 = SUCCESS`.
- Worker before synchronization: `postmerge/backend@fa995bf462aa8135d24f4e9e7059bc24f6992622`.
- Pre-sync comparison against Develop: `136 ahead / 33 behind`; broad historical product/test drift made that worker unsuitable as a bounded integration candidate.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Closed root-cause cluster this run

### Backend worker baseline divergence

Status: `CLOSED BY HISTORY-PRESERVING SYNCHRONIZATION`.

The Backend worker is synchronized to the exact current canonical-green Develop tree while retaining both histories through a normal two-parent merge commit. No force push, history rewrite, product mutation, test mutation, guard relaxation, Skip/XFail, or mutation to `main`/`bnbgrs/ATHENA` is used.

This intentionally removes the broad stale worker file delta from the active candidate surface. Historical Backend commits remain reachable in history but are not reintroduced into the current working tree merely because they existed on the old worker lineage.

## Current backend failure state

- Current Develop exact-SHA Backend failure: none; canonical Quality is green.
- Current Error handoff on Develop reports `OPEN: none`.
- Integrator still identifies BE-046 and BE-052 as Backend-owned gaps requiring a bounded exact-tested candidate before promotion.
- Historical signatures are not reopened without exact-current reproduction.

## Highest next Backend gap

BE-046 remains the next conservative Backend target only if current source/spec evidence still reproduces it on the synchronized baseline. The previous local focused-test path was transiently blocked by DNS resolution of `github.com`; no focused PASS is fabricated and no untested Storage mutation is carried through this synchronization.

Develop now contains `.github/workflows/core-focused-candidate.yml`, proving an exact pull-request-head focused verification pattern. A Backend-focused equivalent may be proposed as a separate bounded systems slice if local DNS remains unavailable; it must not weaken or replace canonical Quality.

## Preserved release guards

- no silent Tor-to-Direct fallback;
- Redirect/Auth/HTTPS/response-size boundaries remain fail-closed;
- WAL maintenance remains safe and SQLite-owned;
- pypdf packaging, Frozen argv and two-EXE topology remain guarded;
- bounded worker ownership/lifecycle and adaptive 2048-context reserve remain guarded;
- Windows lane-lock/path-safety and duplicate-column/Core-startup/storage-bootstrap protections remain intact;
- no Skip/XFail, force push, history rewrite or direct Develop/main integration by Backend.

## Integrator prerequisites

- Treat the synchronization commit as baseline hygiene, not a product feature.
- Do not re-import the old broad Backend worker delta as a unit.
- Any subsequent Backend product candidate must be a small diff from this synchronized baseline, run real focused regressions first, preserve Storage/Recovery/Security invariants, and obtain exact-SHA evidence before READY.
