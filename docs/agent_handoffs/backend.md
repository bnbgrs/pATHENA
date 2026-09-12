# pATHENA Backend & Systems Handoff

## Current baseline

- Integration target: `develop/pathena-next@28b9585b49bf632401340735f05de20d95a70ead`.
- Current Develop canonical Quality: `34679217397 = SUCCESS` on exact SHA `28b9585b49bf632401340735f05de20d95a70ead`.
- Worker branch: `postmerge/backend`.
- Verified Backend product candidate: `0ce1a70d421b41cd0ca4441399d97c82b9849285`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Selected bounded Backend slice

Area: durable scheduled-job missed-run policy core from Beta chapter 12 §§24-28.

Product file: `src/athena/jobs/schedule_policy.py`.
Focused regression: `tests/unit/test_schedule_policy.py`.

The primitive deterministically selects due UTC schedule occurrences for the required policies `skip`, `run_once`, `backfill_all`, and `backfill_bounded`. It excludes future occurrences; rejects duplicate or non-increasing occurrence streams; rejects negative/bool timestamps; and requires a genuine positive integer bound only for `backfill_bounded`.

It intentionally does not implement ScheduleDefinition persistence, occurrence-to-job persistence, queue admission, leases, worker dispatch, or DST recurrence generation. Those remain distinct follow-up slices.

## Exact-SHA verification

Candidate `0ce1a70d421b41cd0ca4441399d97c82b9849285` is fully verified:

- ATHENA Quality Gate `34678280400 = SUCCESS`.
- pATHENA Backend Focused Candidate `34678280408 = SUCCESS`.
- Prior candidate failures are closed: Ruff B905 is explicitly satisfied with `strict=False`, which preserves the intended adjacent-pair comparison because the shifted iterable is intentionally one item shorter.
- No Skip/XFail, guard weakening, assertion deletion, or Storage/Security/Recovery relaxation was used.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Current source-of-truth coordination

- Current Error handoff has no OPEN current regression; historical errors are not reopened without fresh exact-SHA reproduction.
- Current Core handoff owns normal-Hybrid Search facade/application composition and is non-overlapping.
- UI owns visual/workspace work and is non-overlapping.
- Develop has advanced by one Core integration commit since the verified Backend candidate; comparison shows the active Backend product delta remains exactly the two Schedule-policy files.

## Integrator handoff

Promote only the bounded Schedule-policy product/test delta from verified candidate `0ce1a70d421b41cd0ca4441399d97c82b9849285` onto current Develop. Do not import unrelated Backend history.

Required preserved behavior:

- `skip` materializes no missed occurrence;
- `run_once` selects only the newest due occurrence;
- `backfill_all` selects every due occurrence in canonical order;
- `backfill_bounded` selects the oldest due occurrences up to the positive bound;
- future occurrences never materialize;
- invalid ordering, duplicates, bool/negative timestamps and invalid bounds fail closed.

## Next distinct Backend gap

After Integrator consumption, select the highest current Backend/System gap from authoritative handoffs/specs. For the scheduler domain, the next independent bounded slice is persistent `ScheduleDefinition` plus one-job-per-occurrence/idempotency wiring (§§24-25), not rework of the now exact-green policy primitive.

BE-046: no fresh current OPEN exact-SHA reproduction in authoritative Error handoff; do not reopen historically.
BE-052: no fresh current OPEN exact-SHA reproduction in authoritative Error handoff; do not reopen historically. If a future exact-SHA writer-identity regression reappears, treat it as a new current P1.
