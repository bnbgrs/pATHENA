# Quality Gate Incident — Emergency reserve provisioning can create EMERGENCY disk pressure

Date: 2026-08-23

## Status

- Priority: P1 storage-safety boundary
- Ownership: BACKEND
- Quality status: BLOCKED on Backend owner
- Product mutation by Quality: none
- Execution status: static reproduction confirmed; no targeted runtime PASS/FAIL available yet

## Observed HEAD

The defect was revalidated on `agent/pathena` at HEAD `67e15f788d7ba731ede28b1d04efc25769851eaf` in `src/athena/storage/disk_pressure.py` blob `4185677acf6a2427b83cc9bf80c3cd9ccc088fc9`.

## Affected component

- `src/athena/storage/disk_pressure.py`
- `DiskPressureController.ensure_reserve_if_safe()`
- FG-015 / BE-029 / BE-030 bootstrap integration

## Primary defect

`ensure_reserve_if_safe()` decides whether reserve provisioning is safe from the **pre-allocation** pressure state only. Any state other than `EMERGENCY` proceeds directly to `EmergencyReserveStore.ensure()`.

The method does not check whether subtracting the required physical reserve from current free bytes would itself move the volume below the EMERGENCY threshold.

That means reserve creation can consume the exact recovery headroom the reserve is intended to protect.

## Deterministic reproduction by policy arithmetic

For a 100 GiB volume:

- WARNING threshold = 10 GiB
- CRITICAL threshold = 5 GiB
- EMERGENCY threshold = 2 GiB
- required emergency reserve = 1 GiB

At 2.5 GiB free:

1. current pressure = `CRITICAL`, therefore provisioning is allowed;
2. required reserve = 1 GiB;
3. after physical allocation, nominal free space becomes about 1.5 GiB;
4. 1.5 GiB is below the 2 GiB EMERGENCY threshold.

The controller therefore calls a method named `ensure_reserve_if_safe()` in a state where successful provisioning can immediately create an EMERGENCY condition.

## Current code path

```python
assessment = self._assessment()
required = emergency_reserve_size_bytes(assessment.total_bytes)
if assessment.state is DiskPressureState.EMERGENCY:
    return EmergencyReserveProvisionResult(..., status=None)

status = self.reserve_store.ensure(
    required_bytes=required,
    write_chunk_bytes=chunk_bytes,
)
```

There is no pre-allocation headroom check based on `assessment.free_bytes - required`.

## Existing tests

The current tests cover:

- refusing reprovision when already EMERGENCY;
- successful provisioning in a clearly NORMAL state (100 GiB total / 20 GiB free);
- EMERGENCY-only release and reassessment.

They do not cover a non-EMERGENCY pre-state whose reserve allocation would cross the EMERGENCY threshold.

## Recommended Backend fix

Before allocating a missing reserve, calculate a conservative post-allocation free-space value and refuse/defer provisioning if reserve creation would place the volume in EMERGENCY. At minimum:

1. derive `required_bytes`;
2. require `free_bytes >= required_bytes`;
3. classify `free_bytes - required_bytes` with the same threshold function;
4. do not provision if the projected state is EMERGENCY;
5. add a regression case such as 100 GiB total / 2.5 GiB free / 1 GiB reserve;
6. preserve the existing rule that an already-provisioned reserve may remain during normal/critical operation and is released only at EMERGENCY.

If the intended Beta policy requires a stronger post-provision margin than merely staying out of EMERGENCY, encode that explicitly rather than relying on filesystem allocation failure.

## Required verification

After Backend fixes the component:

1. targeted `tests/unit/test_disk_pressure.py` PASS including projected-pressure boundary cases;
2. Ruff/mypy for `disk_pressure.py` and tests;
3. full Linux keep-going Quality gate;
4. FG-015 bootstrap integration test proving startup does not create emergency pressure merely by provisioning the reserve.
