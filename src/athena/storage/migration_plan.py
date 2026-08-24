"""Read-only migration planning from an ATHENA database preflight report."""

from __future__ import annotations

from dataclasses import dataclass

from athena.storage.migration_safety import MigrationDescriptor
from athena.storage.recovery import DatabasePreflightReport
from athena.storage.schema_contract import SCHEMA_VERSION


class MigrationPlanError(RuntimeError):
    """Raised when startup migration planning cannot classify a database safely."""


@dataclass(frozen=True, slots=True)
class MigrationPlan:
    migration_required: bool
    descriptor: MigrationDescriptor | None

    def __post_init__(self) -> None:
        if not isinstance(self.migration_required, bool):
            raise TypeError("Migration plan migration_required must be bool.")
        if self.migration_required:
            if not isinstance(self.descriptor, MigrationDescriptor):
                raise ValueError("Required migration plan must carry a descriptor.")
        elif self.descriptor is not None:
            raise ValueError("Non-migration plan must not carry a descriptor.")


def plan_database_migration(report: DatabasePreflightReport) -> MigrationPlan:
    """Classify startup as create/current/migrate without opening a writer."""
    if not isinstance(report, DatabasePreflightReport):
        raise TypeError("report must be DatabasePreflightReport.")
    if not report.exists:
        return MigrationPlan(migration_required=False, descriptor=None)
    if report.schema_version is None:
        raise MigrationPlanError("Existing database preflight has no schema version.")
    if report.schema_version == SCHEMA_VERSION:
        return MigrationPlan(migration_required=False, descriptor=None)
    if not 1 <= report.schema_version < SCHEMA_VERSION:
        raise MigrationPlanError(
            "Existing database schema version has no supported clone migration plan."
        )

    descriptor = MigrationDescriptor(
        migration_id=f"schema-v{report.schema_version}-to-v{SCHEMA_VERSION}",
        from_version=report.schema_version,
        to_version=SCHEMA_VERSION,
        reversible=False,
        requires_clone=True,
        estimated_space_factor=1.25,
        requires_rebuild=False,
    )
    return MigrationPlan(migration_required=True, descriptor=descriptor)
