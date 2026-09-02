from __future__ import annotations

import pytest

from athena.storage.migration_safety import (
    MigrationDescriptor,
    MigrationSpacePreflight,
    assess_migration_free_space,
    required_migration_free_space,
)

_MIB = 1024 * 1024


def test_required_migration_space_matches_beta_policy_exactly() -> None:
    database_size = 100 * _MIB
    reserve = 64 * _MIB

    assert required_migration_free_space(
        database_size_bytes=database_size,
        emergency_reserve_bytes=reserve,
    ) == (100 + 25 + 512 + 64) * _MIB


def test_required_migration_space_rounds_quarter_up_without_float_conversion() -> None:
    assert required_migration_free_space(
        database_size_bytes=1,
        emergency_reserve_bytes=0,
    ) == 1 + 1 + 512 * _MIB


def test_required_migration_space_supports_huge_integer_sizes() -> None:
    huge = 10**400

    result = required_migration_free_space(
        database_size_bytes=huge,
        emergency_reserve_bytes=7,
    )

    assert result == huge + (huge + 3) // 4 + 512 * _MIB + 7


@pytest.mark.parametrize("value", [True, False, -1, 1.5, "1", None])
def test_required_migration_space_rejects_invalid_sizes(value: object) -> None:
    with pytest.raises(ValueError, match="non-negative integer"):
        required_migration_free_space(
            database_size_bytes=value,  # type: ignore[arg-type]
            emergency_reserve_bytes=0,
        )


def test_space_assessment_is_sufficient_at_exact_boundary() -> None:
    required = required_migration_free_space(
        database_size_bytes=10,
        emergency_reserve_bytes=20,
    )

    report = assess_migration_free_space(
        database_size_bytes=10,
        available_bytes=required,
        emergency_reserve_bytes=20,
    )

    assert report.sufficient is True
    assert report.required_free_bytes == required


def test_space_assessment_is_insufficient_one_byte_below_boundary() -> None:
    required = required_migration_free_space(
        database_size_bytes=10,
        emergency_reserve_bytes=20,
    )

    report = assess_migration_free_space(
        database_size_bytes=10,
        available_bytes=required - 1,
        emergency_reserve_bytes=20,
    )

    assert report.sufficient is False


def test_space_report_rejects_inconsistent_derived_fields() -> None:
    required = required_migration_free_space(
        database_size_bytes=10,
        emergency_reserve_bytes=20,
    )

    with pytest.raises(ValueError, match="does not match"):
        MigrationSpacePreflight(
            database_size_bytes=10,
            available_bytes=required,
            emergency_reserve_bytes=20,
            required_free_bytes=required + 1,
            sufficient=True,
        )

    with pytest.raises(ValueError, match="disagrees"):
        MigrationSpacePreflight(
            database_size_bytes=10,
            available_bytes=required,
            emergency_reserve_bytes=20,
            required_free_bytes=required,
            sufficient=False,
        )


def test_migration_descriptor_requires_forward_canonical_metadata() -> None:
    descriptor = MigrationDescriptor(
        migration_id="schema-v40-to-v41",
        from_version=40,
        to_version=41,
        reversible=False,
        requires_clone=True,
        estimated_space_factor=1.25,
        requires_rebuild=False,
    )

    assert descriptor.from_version == 40
    assert descriptor.to_version == 41


@pytest.mark.parametrize(
    "overrides",
    [
        {"migration_id": " schema-v40-to-v41"},
        {"from_version": True},
        {"to_version": 40},
        {"reversible": 1},
        {"requires_clone": 1},
        {"estimated_space_factor": float("nan")},
        {"estimated_space_factor": float("inf")},
        {"estimated_space_factor": 0.99},
        {"requires_rebuild": 0},
    ],
)
def test_migration_descriptor_rejects_invalid_contract(overrides: dict[str, object]) -> None:
    values: dict[str, object] = {
        "migration_id": "schema-v40-to-v41",
        "from_version": 40,
        "to_version": 41,
        "reversible": False,
        "requires_clone": True,
        "estimated_space_factor": 1.25,
        "requires_rebuild": False,
    }
    values.update(overrides)

    with pytest.raises((TypeError, ValueError)):
        MigrationDescriptor(**values)  # type: ignore[arg-type]
