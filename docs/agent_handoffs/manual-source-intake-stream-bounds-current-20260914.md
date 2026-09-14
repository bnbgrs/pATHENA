# Source Intake + Stream Bounds — current Develop reconstruction

Date: 2026-09-14
Base: `develop/pathena-next@f8a25be7fd7df9f2a8ca281a1567f79ddaabcfb6`
Source candidate: PR #212 exact head `eee77b26905186ebde3e8e625347d6faedee5895`

## Purpose

Reconstruct the complete bounded Source intake end state from canonical-green PR #212 directly on the latest Develop head, without replaying historical commits and without touching later Knowledge/provider additions.

## Compatibility proof

#212 was based on `develop/pathena-next@42614da4d235c2613b7a683d357a5af17a271817` and its exact head passed canonical ATHENA Quality #5325 SUCCESS.

A direct compare from that base to current Develop shows only Knowledge/API handoff changes plus the new `src/athena/source/representation_providers.py` provider-contract file and its tests. None of #212's ten owned files changed on Develop. Therefore this reconstruction can place the exact #212 end-state blobs onto the current tree without manual product reconciliation.

## Retained behavior

- deterministic file/multi-file/folder intake;
- bounded `FOLLOW_INSIDE_ROOT` with selected/display path separated from canonical capture target;
- re-resolution before capture so target swaps and selected-root escapes fail closed;
- benign in-root directory aliases remain non-blocking duplicates while active-recursion cycles remain blocking;
- direct system-metadata-root filtering with explicit opt-in support;
- exact protected-scope forwarding;
- optional `max_file_bytes` propagated to normal and protected byte readers;
- bool/non-int/negative byte limits fail closed;
- readers probe no more than remaining byte budget plus one byte;
- the cumulative limit is enforced before plain staging writes and before protected encryption;
- `max_file_bytes=0` is enforced with a one-byte probe;
- partial staging is removed on breach and no Blob/Source is committed;
- a stream that grows beyond the preflight bound is treated as source mutation, preserving intake's existing exactly-one controlled retry.

## Files

The ten product/test/handoff blobs are exact copies of #212 head `eee77b269…`. This file is the only new reconstruction-only documentation.

## Integration rule

Keep draft until current Develop push Quality and this exact reconstructed head are terminal green. Recheck Develop identity, exact diff and active Source/provider ownership immediately before merge. If Develop changes any owned Source file first, stop and reconcile rather than merging stale evidence.
