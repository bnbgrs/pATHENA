"""Pure safety contracts for clone-based ATHENA schema migration."""

from __future__ import annotations

import math
from dataclasses import dataclass

_MIB = 1024 * 1024
_MIGRATION_FIXED_HEADROOM_BYTES = 512 * _MIB


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return value


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be a positive integer.")
    return value


def _canonical_identifier(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text.")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} must not be empty.")
    if normalized != value:
        raise ValueError(f"{label} must use canonical trimmed text.")
    return normalized


@dataclass(frozen=True, slots=True)
class MigrationDescriptor:
    """Versioned migration metadata required by the Beta storage contract."""

    migration_id: str
    from_version: int
    to_version: int
    reversible: bool
    requires_clone: bool
    estimated_space_factor: float
    requires_rebuild: bool

    def __post_init__(self) -> None:
        _canonical_identifier(self.migration_id, "Migration id")
        from_version = _positive_int(self.from_version, "Migration from_version")
        to_version = _positive_int(self.to_version, "Migration to_version")
        if to_version <= from_version:
            raise ValueError("Migration to_version must be greater than from_version.")
        if not isinstance(self.reversible, bool):
            raise TypeError("Migration reversible must be bool.")
        if not isinstance(self.requires_clone, bool):
            raise TypeError("Migration requires_clone must be bool.")
        if (
            isinstance(self.estimated_space_factor, bool)
            or not isinstance(self.estimated_space_factor, (int, float))
        ):
            raise TypeError("Migration estimated_space_factor must be numeric.")
        try:
            factor = float(self.estimated_space_factor)
        except OverflowError as exc:
            raise ValueError("Migration estimated_space_factor must be finite.") from exc
        if not math.isfinite(factor) or factor < 1.0:
            raise ValueError(
                "Migration estimated_space_factor must be finite and at least 1.0."
            )
        if not isinstance(self.requires_rebuild, bool):
            raise TypeError("Migration requires_rebuild must be bool.")


@dataclass(frozen=True, slots=True)
class MigrationSpacePreflight:
    """Deterministic disk-space decision before creating a migration clone."""

    database_size_bytes: int
    available_bytes: int
    emergency_reserve_bytes: int
    required_free_bytes: int
    sufficient: bool

    def __post_init__(self) -> None:
        database_size = _nonnegative_int(
            self.database_size_bytes,
            "Migration database_size_bytes",
        )
        available = _nonnegative_int(
            self.available_bytes,
            "Migration available_bytes",
        )
        reserve = _nonnegative_int(
            self.emergency_reserve_bytes,
            "Migration emergency_reserve_bytes",
        )
        required = _nonnegative_int(
            self.required_free_bytes,
            "Migration required_free_bytes",
        )
        expected = required_migration_free_space(
            database_size_bytes=database_size,
            emergency_reserve_bytes=reserve,
        )
        if required != expected:
            raise ValueError(
                "Migration required_free_bytes does not match the Beta free-space policy."
            )
        if not isinstance(self.sufficient, bool):
            raise TypeError("Migration sufficient must be bool.")
        if self.sufficient is not (available >= required):
            raise ValueError("Migration sufficient flag disagrees with available space.")


def required_migration_free_space(
    *,
    database_size_bytes: int,
    emergency_reserve_bytes: int,
) -> int:
    """Return Beta-03 free-space requirement for one clone migration.

    Required free space is the current database size, plus a 25 percent safety
    margin rounded up, plus 512 MiB fixed headroom, plus the configured emergency
    reserve. The calculation is integer-only so very large sizes never lose
    precision through float conversion.
    """
    database_size = _nonnegative_int(
        database_size_bytes,
        "Migration database_size_bytes",
    )
    reserve = _nonnegative_int(
        emergency_reserve_bytes,
        "Migration emergency_reserve_bytes",
    )
    safety_margin = (database_size + 3) // 4
    return database_size + safety_margin + _MIGRATION_FIXED_HEADROOM_BYTES + reserve


def assess_migration_free_space(
    *,
    database_size_bytes: int,
    available_bytes: int,
    emergency_reserve_bytes: int,
) -> MigrationSpacePreflight:
    """Build the fail-closed disk-space decision used by migration orchestration."""
    database_size = _nonnegative_int(
        database_size_bytes,
        "Migration database_size_bytes",
    )
    available = _nonnegative_int(
        available_bytes,
        "Migration available_bytes",
    )
    reserve = _nonnegative_int(
        emergency_reserve_bytes,
        "Migration emergency_reserve_bytes",
    )
    required = required_migration_free_space(
        database_size_bytes=database_size,
        emergency_reserve_bytes=reserve,
    )
    return MigrationSpacePreflight(
        database_size_bytes=database_size,
        available_bytes=available,
        emergency_reserve_bytes=reserve,
        required_free_bytes=required,
        sufficient=available >= required,
    )
