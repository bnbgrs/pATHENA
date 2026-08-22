"""Local installation and runtime diagnostics for pATHENA."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from athena.config.settings import AthenaSettings, ConfigurationError
from athena.core.application import AthenaApplication
from athena.model.adapters.lm_studio import LMStudioProvider
from athena.model.domain import ProviderHealthStatus
from athena.storage.paths import RuntimePaths
from athena.storage.recovery import DatabaseRecoveryRequiredError, inspect_database_read_only
from athena.version import __version__

_MIN_FREE_BYTES_WARNING = 2 * 1024 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class DoctorCheck:
    name: str
    status: str
    detail: str


@dataclass(frozen=True, slots=True)
class DoctorReport:
    checks: tuple[DoctorCheck, ...]
    core_ready: bool
    model_ready: bool


def _check_runtime_write(root: Path) -> DoctorCheck:
    try:
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix="athena-doctor-",
            suffix=".tmp",
            dir=root,
            delete=True,
        ) as handle:
            handle.write(b"athena-doctor")
            handle.flush()
    except OSError as exc:
        return DoctorCheck("runtime-write", "FAIL", f"{root}: {exc}")
    return DoctorCheck("runtime-write", "PASS", str(root))


def _check_disk_space(root: Path) -> DoctorCheck:
    try:
        usage = shutil.disk_usage(root)
    except OSError as exc:
        return DoctorCheck("disk-space", "FAIL", f"{root}: {exc}")
    free_gib = usage.free / (1024**3)
    status = "WARN" if usage.free < _MIN_FREE_BYTES_WARNING else "PASS"
    return DoctorCheck("disk-space", status, f"{free_gib:.1f} GiB free at {root}")


def _check_optional_storage_root(
    name: str,
    root: Path | None,
    *,
    missing_status: str,
    missing_detail: str,
) -> DoctorCheck:
    if root is None:
        return DoctorCheck(name, missing_status, missing_detail)
    if root.is_symlink():
        return DoctorCheck(name, "WARN", f"configured root is a symbolic link: {root}")
    if not root.is_dir():
        return DoctorCheck(name, "WARN", f"configured root is unavailable: {root}")
    return DoctorCheck(name, "PASS", str(root))


def _check_database(paths: RuntimePaths) -> DoctorCheck:
    try:
        report = inspect_database_read_only(paths.database_path)
    except DatabaseRecoveryRequiredError as exc:
        return DoctorCheck("database-preflight", "FAIL", str(exc))
    if not report.exists:
        return DoctorCheck(
            "database-preflight",
            "PASS",
            f"new database will be created at {report.path}",
        )
    sidecars = []
    if report.wal_present:
        sidecars.append("WAL")
    if report.shm_present:
        sidecars.append("SHM")
    suffix = "" if not sidecars else f" sidecars={','.join(sidecars)}"
    return DoctorCheck(
        "database-preflight",
        "PASS",
        f"schema={report.schema_version} path={report.path}{suffix}",
    )


def _check_model(settings: AthenaSettings) -> DoctorCheck:
    provider = LMStudioProvider(
        base_url=settings.lm_studio_base_url,
        timeout_seconds=settings.model_request_timeout_seconds,
        generation_timeout_seconds=settings.model_generation_timeout_seconds,
    )
    health = provider.health()
    if health.status is ProviderHealthStatus.READY:
        try:
            models = provider.discover_models()
        except Exception as exc:
            return DoctorCheck("lm-studio", "FAIL", f"discovery failed: {exc}")

        llms = tuple(model for model in models if model.model_type == "llm")
        loaded_llms = tuple(model for model in llms if model.loaded)
        if not loaded_llms:
            detail = (
                f"server ready at {provider.base_url}; models={len(models)} "
                f"llms={len(llms)} loaded_llms=0; load a local LLM in LM Studio"
            )
            return DoctorCheck("lm-studio", "WARN", detail)

        loaded_ids = ", ".join(model.backend_model_id for model in loaded_llms[:3])
        if len(loaded_llms) > 3:
            loaded_ids += f", +{len(loaded_llms) - 3} more"
        detail = (
            f"chat ready at {provider.base_url}; models={len(models)} "
            f"loaded_llms={len(loaded_llms)} [{loaded_ids}]"
        )
        return DoctorCheck("lm-studio", "PASS", detail)
    detail = health.detail or f"provider status is {health.status.value}"
    return DoctorCheck("lm-studio", "WARN", detail)


def run_doctor(
    settings: AthenaSettings,
    *,
    startup_smoke: bool = True,
) -> DoctorReport:
    checks: list[DoctorCheck] = []

    python_ok = sys.version_info[:2] == (3, 12)
    checks.append(
        DoctorCheck(
            "python",
            "PASS" if python_ok else "FAIL",
            sys.version.replace("\n", " "),
        )
    )

    paths = RuntimePaths.from_settings(settings)
    checks.append(DoctorCheck("local-root", "PASS", str(paths.local_root)))
    write_check = _check_runtime_write(paths.local_root)
    checks.append(write_check)
    if write_check.status == "PASS":
        checks.append(_check_disk_space(paths.local_root))
    else:
        checks.append(
            DoctorCheck("disk-space", "SKIP", "runtime root is not writable")
        )

    checks.append(
        _check_optional_storage_root(
            "archive-root",
            paths.archive_root,
            missing_status="PASS",
            missing_detail="not configured; source bytes remain in durable local spool",
        )
    )
    checks.append(
        _check_optional_storage_root(
            "backup-root",
            paths.backup_root,
            missing_status="WARN",
            missing_detail="not configured; local pATHENA data is not externally backed up",
        )
    )
    checks.append(
        _check_optional_storage_root(
            "projection-root",
            paths.projection_root,
            missing_status="PASS",
            missing_detail="not configured; external projection is optional",
        )
    )

    database_check = _check_database(paths)
    checks.append(database_check)

    startup_ok = True
    if startup_smoke and write_check.status == "PASS" and database_check.status == "PASS":
        app = AthenaApplication(settings=settings)
        try:
            app.start(run_startup_maintenance=False)
        except Exception as exc:
            startup_ok = False
            checks.append(DoctorCheck("core-startup", "FAIL", f"{type(exc).__name__}: {exc}"))
        else:
            checks.append(DoctorCheck("core-startup", "PASS", app.state.value))
        finally:
            if app.state.value != "stopped":
                try:
                    app.stop()
                except Exception as exc:
                    startup_ok = False
                    checks.append(
                        DoctorCheck(
                            "core-shutdown",
                            "FAIL",
                            f"{type(exc).__name__}: {exc}",
                        )
                    )
                else:
                    checks.append(DoctorCheck("core-shutdown", "PASS", app.state.value))
    elif startup_smoke:
        startup_ok = False
        checks.append(
            DoctorCheck(
                "core-startup",
                "SKIP",
                "prerequisite runtime/database check failed",
            )
        )

    model_check = _check_model(settings)
    checks.append(model_check)

    core_ready = (
        python_ok
        and write_check.status == "PASS"
        and database_check.status == "PASS"
        and startup_ok
    )
    model_ready = model_check.status == "PASS"
    return DoctorReport(
        checks=tuple(checks),
        core_ready=core_ready,
        model_ready=model_ready,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="athena-doctor",
        description="Check whether the local pATHENA runtime is ready.",
    )
    parser.add_argument(
        "--no-startup-smoke",
        action="store_true",
        help="Skip starting and stopping the ATHENA Core during diagnostics.",
    )
    parser.add_argument(
        "--require-model",
        action="store_true",
        help="Return a failing exit code unless LM Studio has a loaded local LLM.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    print(f"pATHENA doctor {__version__}")
    try:
        settings = AthenaSettings.from_environment()
    except ConfigurationError as exc:
        print(f"[FAIL] configuration: {exc}")
        return 2

    report = run_doctor(settings, startup_smoke=not args.no_startup_smoke)
    for check in report.checks:
        print(f"[{check.status}] {check.name}: {check.detail}")

    print(f"Core ready: {'YES' if report.core_ready else 'NO'}")
    print(f"Local chat model ready: {'YES' if report.model_ready else 'NO'}")

    if not report.core_ready:
        return 2
    if args.require_model and not report.model_ready:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
