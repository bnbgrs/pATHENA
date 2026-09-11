from __future__ import annotations

from pathlib import Path

import pytest

from athena.storage.migration_plan import MigrationPlanError, plan_database_migration
from athena.storage.recovery import (
    DatabaseFileIdentity,
    DatabaseFileSetIdentity,
    DatabasePreflightReport,
)
from athena.storage.schema_contract import ATHENA_APPLICATION_ID, SCHEMA_VERSION


def _identity(path: Path, *, exists: bool) -> DatabaseFileIdentity:
    return DatabaseFileIdentity(
        path=path,
        exists=exists,
        device=1 if exists else None,
        inode=1 if exists else None,
        size=4096 if exists else None,
        mtime_ns=1 if exists else None,
        ctime_ns=1 if exists else None,
    )


def _report(*, exists: bool, schema_version: int | None) -> DatabasePreflightReport:
    path = Path("/tmp/athena.db")
    return DatabasePreflightReport(
        path=path,
        exists=exists,
        application_id=ATHENA_APPLICATION_ID if exists else None,
        schema_version=schema_version,
        wal_present=False,
        shm_present=False,
        file_set=DatabaseFileSetIdentity(
            primary=_identity(path, exists=exists),
            wal=_identity(path.with_name(f"{path.name}-wal"), exists=False),
            shm=_identity(path.with_name(f"{path.name}-shm"), exists=False),
        ),
    )


def test_missing_database_does_not_require_migration() -> None:
    plan = plan_database_migration(_report(exists=False, schema_version=None))

    assert plan.migration_required is False
    assert plan.descriptor is None


def test_current_database_does_not_require_migration() -> None:
    plan = plan_database_migration(
        _report(exists=True, schema_version=SCHEMA_VERSION)
    )

    assert plan.migration_required is False
    assert plan.descriptor is None


def test_legacy_database_gets_clone_required_plan_to_current_schema() -> None:
    plan = plan_database_migration(_report(exists=True, schema_version=1))

    assert plan.migration_required is True
    assert plan.descriptor is not None
    assert plan.descriptor.from_version == 1
    assert plan.descriptor.to_version == SCHEMA_VERSION
    assert plan.descriptor.requires_clone is True
    assert plan.descriptor.migration_id == f"schema-v1-to-v{SCHEMA_VERSION}"


def test_intermediate_database_gets_exact_source_version_plan() -> None:
    source_version = SCHEMA_VERSION - 1
    plan = plan_database_migration(
        _report(exists=True, schema_version=source_version)
    )

    assert plan.descriptor is not None
    assert plan.descriptor.from_version == source_version
    assert plan.descriptor.to_version == SCHEMA_VERSION


@pytest.mark.parametrize("schema_version", [0, SCHEMA_VERSION + 1])
def test_unsupported_existing_version_is_rejected(schema_version: int) -> None:
    with pytest.raises(MigrationPlanError, match="no supported clone migration plan"):
        plan_database_migration(
            _report(exists=True, schema_version=schema_version)
        )
