# Principal Engineering Run Handoff — 2026-10-02 (Sol 2)

## Baseline and synchronization

- Integration target inspected: `develop/pathena-next`.
- Current integration SHA for this run: `467ef434236c320e4afe9d21a39c20a4a2b75728`.
- Open PRs, active branches, recent commits, CI, issues and established handoff/coordination docs were inspected before code changes.
- Local checkout/execution is unavailable in this runner because `github.com` DNS resolution is blocked. No local pytest, Desktop, Windows or UI PASS is claimed.
- GitHub Actions exact-head Quality remains the executable validation source for the two implementation slices below.

## Slice 1 — External Access Gateway

### PR / branch

- PR: #369 — **External: preflight research batches and audit redirect failures**
- Branch: `fix/external-access-integrity-boundaries-20261002-sol`
- Head: `c1c69e3c6f42b601213aa3cead67e64ee977c7a7`
- Base: `develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`
- Exact-head Quality run: `36939341307` — queued at handoff time.

### Ausgangslage

`ExternalResearchService.enqueue()` could start Source captures before the complete URL batch had been validated. A later malformed/out-of-scope URL could therefore fail the operation after earlier Source side effects already existed.

Redirect terminal failures were also not fully auditable:
- redirect-limit exhaustion raised without a failed external-access audit event;
- a transport-reported `final_url` was revalidated, but the final denial bypassed the gateway's audited-denial wrapper.

### Root cause

Authorization was validated incrementally at capture time instead of preflighting the complete Research request set before the first mutation. Separately, two terminal redirect paths did not consistently pass through the same audit boundary used by normal authorization failures.

### Änderungen

- Added a non-network URL authorization/destination validation boundary.
- External Research now validates the URL container and every URL before the first Source capture.
- Raw `str`/`bytes` containers and non-string URL members are rejected before capture.
- Redirect-limit exhaustion persists `reason_code=redirect_limit_exceeded` before raising.
- Transport-reported final destination validation now goes through the audited denial path.
- Added focused regressions for no-partial-capture preflight and both redirect audit cases.

### Dateien

- `src/athena/external/gateway.py`
- `tests/unit/test_external_access_integrity_boundaries.py`

### Parallel ownership / collision handling

During the run, PR #365 appeared:
- #365 — **External: fail closed on corrupt authorization persistence**
- branch `fix/external-auth-persistence-boundaries-20261002-sol`
- head `0543b49df909aaa7df39323db9b49f14551dc666`

The first version of #369 also contained persisted-authorization integrity hardening. That overlap was explicitly removed from #369's final diff after #365 appeared. No force push/reset was used. #369 now contains only complementary batch/redirect/audit work.

Because #365 and #369 still touch the same gateway file, recommended integration is:
1. qualify/integrate #365;
2. refresh #369 on the resulting Develop;
3. preserve #369's `validate_url`, Research batch preflight and redirect/audit hunks;
4. rerun exact-head Quality.

## Slice 2 — Resource Manager

### PR / branch

- PR: #388 — **Resources: harden interactive leases and persisted policy**
- Branch: `fix/resource-interactive-lease-filesystem-20261002-sol`
- Head: `8a5a70c8f976cd498d6f9eb6c31f558669bc64c8`
- Base: `develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`
- Exact-head Quality run: `36940408876` — queued at handoff time.

### Ausgangslage

Interactive-demand leases used an unchecked `state/interactive-demand` directory and ordinary renewal semantics. A pre-existing symlink/reparse-point root could redirect lease operations, and an old in-memory lease could recreate a released lease or overwrite a newer renewal.

`resource_policy` was also reconstructed coercively with `int()/float()/bytes()`. SQLite may retain a REAL value in an INTEGER-affinity column while satisfying the current nonnegative CHECK; coercing `0.5` to `int` silently changes runtime admission policy to `0`.

### Root cause

The lease lifecycle trusted pathname state and in-memory lease identity more than the persisted operational record. Policy reads trusted SQLite affinity instead of validating runtime storage types at the domain boundary.

### Änderungen

- Lease root is validated/created through existing `durable_mkdir`; pre-existing symlink/reparse-point roots fail closed.
- Acquire/renew publication uses existing `durable_write_bytes`.
- Link-backed individual lease entries are ignored rather than followed.
- Renewal must match the currently persisted lease ID, purpose, acquisition time, expiry and duration.
- Renewal after release is rejected.
- An older lease revision cannot overwrite a newer persisted renewal in the normal sequential lifecycle.
- Persisted ResourceMode, integer headrooms/timestamp, GPU threshold and actor UUID storage are validated before `ResourcePolicy` construction.
- Fractional values in INTEGER policy fields now fail closed instead of being truncated.

### Dateien

Final PR diff is intentionally limited to:
- `src/athena/resources/manager.py`
- `tests/unit/test_resource_interactive_lease_filesystem.py`
- `tests/unit/test_resource_policy_persistence_boundaries.py`

### Parallel ownership / collision handling

During this run, Storage PR #385 began modifying `src/athena/storage/durable_fs.py`:
- #385 — **Storage: verify append-only long-term replication publication**
- branch `fix/structured-replication-publication-20261002-sol`
- head `d2c29db93a69abee78ec26d14515d4c4ae97bb4d`
- stacked on `integration/canonical-commit-bundle-fresh-20261001`

A shared identity-bound unlink helper was briefly explored on the Resource branch. Once #385 ownership appeared, the entire `durable_fs.py` and associated durable-unlink test diff was restored/removed from #388. #388 has no final `durable_fs.py` change and does not compete with the Storage owner.

### Known residual

`release_interactive_demand()` and expired-lease cleanup still perform leaf `unlink` after validating the lease root. Pre-existing redirected roots are blocked, but a malicious concurrent parent replacement exactly between validation and unlink is not claimed solved.

If Storage wants to close that remaining TOCTOU window, add a shared identity-bound delete primitive in the Storage-owned durable-fs layer and then switch Resource cleanup/release to it. Do not duplicate that primitive in #388 while #385 owns `durable_fs.py`.

A separate concurrent renew-vs-release race can still exist if release happens after renewal validates the persisted lease but before atomic renewal publication. The current fix prevents stale/released renewal in normal sequential lifecycle; it is not a cross-process CAS/locking implementation.

## Validation status

### Confirmed

- Both implementation PRs are based on the same current Develop SHA.
- Final diffs were inspected after collision cleanup.
- #369 final diff: 2 files, no persisted-authorization overlap with #365.
- #388 final diff: 3 files, no `durable_fs.py` overlap with #385.
- No force push, hard reset, branch deletion or foreign branch rewrite was used.

### Not yet confirmed

- Exact-head Quality for #369: queued.
- Exact-head Quality for #388: queued.
- No local pytest/type/lint run due unavailable local checkout/network.
- No Desktop/UI/manual Windows runtime validation was possible in this runner.
- Neither PR should be described as CI-green until the queued exact-head runs are terminal PASS.

## Next concrete steps

1. Watch Quality run `36939341307` for #369. If it fails, inspect the failing job/log and fix only the exact-head failure.
2. Watch Quality run `36940408876` for #388. Same rule: fix real failures, do not bypass gates.
3. Coordinate #365 before #369 because both modify `gateway.py`; refresh #369 after #365 integration.
4. Keep #388 independent from #385. If an identity-bound delete primitive lands from Storage later, add a small follow-up Resource integration for the residual unlink race.
5. After CI is green, run relevant manual/Windows validation where a real checkout is available:
   - External Research batch with first valid + second unauthorized URL: zero captured Sources expected;
   - redirect loop: failed audit event expected;
   - transport final URL outside host scope: denied audit event expected;
   - Resource lease acquire/renew/release and stale renewal;
   - resource policy corruption/admission fail-closed.
6. Do not re-implement the persistence work already owned by #365 or the shared durable-fs work owned by #385.

## Run result

This run produced two bounded implementation PRs covering multiple root causes, resolved two live ownership collisions without destructive Git operations, and left exact integration/testing dependencies explicit for the next bot.
