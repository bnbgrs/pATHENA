"""Ordered storage bootstrap before ATHENA opens its live SQLite writer."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase
from athena.storage.disk_pressure import (
    DiskPressureController,
    DiskPressureState,
    EmergencyReserveProvisionResult,
)
from athena.storage.durable_fs import durable_mkdir, is_link_boundary
from athena.storage.migration_coordinator import (
    MigrationCoordinatorResult,
    run_clone_migration,
)
from athena.storage.migration_executor import migrate_schema_candidate
from athena.storage.migration_plan import MigrationPlan, plan_database_migration
from athena.storage.migration_recovery import (
    MigrationRecoveryAssessment,
    MigrationRecoveryState,
    assess_migration_recovery,
)
from athena.storage.paths import RuntimePaths
from athena.storage.recovery import DatabasePreflightReport, inspect_database_read_only
from athena.storage.runtime import RuntimeLayoutService


class StorageBootstrapError(RuntimeError):
    """Raised when writable storage startup cannot proceed safely."""


class StorageBootstrapRecoveryRequiredError(StorageBootstrapError):
    """Existing migration artifacts require explicit recovery review."""


class StorageBootstrapReadOnlyRequiredError(StorageBootstrapError):
    """Disk pressure requires read-only safe mode instead of writable startup."""


MigrationRunner = Callable[..., MigrationCoordinatorResult]


class StorageBootstrapService:
    """Own the safe ordering for local layout, reserve, migration and DB startup."""

    name = "storage-bootstrap"

    def __init__(
        self,
        *,
        paths: RuntimePaths,
        database: SQLiteDatabase,
        disk_pressure: DiskPressureController | None = None,
        migration_root: Path | None = None,
        migration_runner: MigrationRunner = run_clone_migration,
    ) -> None:
        if not isinstance(paths, RuntimePaths):
            raise TypeError("Storage bootstrap paths must be RuntimePaths.")
        if not isinstance(database, SQLiteDatabase):
            raise TypeError("Storage bootstrap database must be SQLiteDatabase.")
        if disk_pressure is not None and not isinstance(
            disk_pressure,
            DiskPressureController,
        ):
            raise TypeError(
                "Storage bootstrap disk_pressure must be DiskPressureController or None."
            )
        root = (
            paths.state_root / "migration"
            if migration_root is None
            else migration_root.expanduser()
        )
        if not isinstance(root, Path) or not root.is_absolute():
            raise ValueError("Storage bootstrap migration_root must be absolute.")
        if not callable(migration_runner):
            raise TypeError("Storage bootstrap migration_runner must be callable.")

        self.paths = paths
        self.database = database
        self.layout = RuntimeLayoutService(paths)
        self.disk_pressure = disk_pressure or DiskPressureController(paths.state_root)
        self.migration_root = root
        self._migration_runner = migration_runner
        self.preflight: DatabasePreflightReport | None = None
        self.migration_plan: MigrationPlan | None = None
        self.recovery: MigrationRecoveryAssessment | None = None
        self.reserve: EmergencyReserveProvisionResult | None = None
        self.migration_result: MigrationCoordinatorResult | None = None
        self._started = False

    def _ensure_migration_root(self) -> None:
        if self.migration_root.exists():
            if is_link_boundary(self.migration_root) or not self.migration_root.is_dir():
                raise StorageBootstrapError(
                    "Storage bootstrap migration root is not a safe directory."
                )
            return
        try:
            durable_mkdir(self.migration_root, parents=False, exist_ok=False)
        except OSError as exc:
            raise StorageBootstrapError(
                "Storage bootstrap migration root could not be created durably."
            ) from exc

    def _executor(self, candidate_db: Path) -> None:
        migrate_schema_candidate(candidate_db, created_at_us=utc_now_us())

    def start(self) -> None:
        if self._started:
            return

        self.layout.start()
        self._ensure_migration_root()

        preflight = inspect_database_read_only(self.paths.database_path)
        plan = plan_database_migration(preflight)
        recovery = assess_migration_recovery(
            source_db=self.paths.database_path,
            migration_root=self.migration_root,
        )

        if recovery.requires_manual_review:
            raise StorageBootstrapRecoveryRequiredError(
                "ATHENA migration artifacts require recovery review before writable startup: "
                f"{recovery.state.value}."
            )
        if plan.migration_required and recovery.state is not MigrationRecoveryState.NONE:
            raise StorageBootstrapRecoveryRequiredError(
                "ATHENA will not start a new migration while completed migration artifacts "
                "remain attached to a legacy active database."
            )

        reserve = self.disk_pressure.ensure_reserve_if_safe()
        if reserve.assessment.state is DiskPressureState.EMERGENCY:
            raise StorageBootstrapReadOnlyRequiredError(
                "ATHENA active state volume is in EMERGENCY disk pressure; writable startup "
                "is refused so released reserve space remains available for recovery."
            )

        migration_result: MigrationCoordinatorResult | None = None
        if plan.migration_required:
            descriptor = plan.descriptor
            if descriptor is None:
                raise StorageBootstrapError(
                    "Required migration plan is missing its descriptor."
                )
            migration_result = self._migration_runner(
                source_db=self.paths.database_path,
                migration_root=self.migration_root,
                descriptor=descriptor,
                emergency_reserve_bytes=reserve.required_bytes,
                started_at_us=utc_now_us(),
                executor=self._executor,
            )

        self.database.configure_noncritical_write_gate(
            self.disk_pressure.assert_noncritical_write_allowed
        )
        self.database.start()
        self.preflight = preflight
        self.migration_plan = plan
        self.recovery = recovery
        self.reserve = reserve
        self.migration_result = migration_result
        self._started = True

    def stop(self) -> None:
        if not self._started:
            return
        self.database.stop()
        self.layout.stop()
        self._started = False
