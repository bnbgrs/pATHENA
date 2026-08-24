"""Conservative resource probes and scheduler admission policy."""

from __future__ import annotations

import ctypes
import json
import math
import os
import shutil
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path
from typing import Protocol

from athena.chat.service import ChatService
from athena.common.ids import new_uuid7, uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.jobs.capabilities import requires_provider_isolation
from athena.jobs.models import JobPriority, JobRecord
from athena.model.ports import ChatModelProvider
from athena.storage.database import SQLiteDatabase
from athena.storage.paths import RuntimePaths


class ResourceMode(str, Enum):
    BALANCED = "balanced"
    QUIET = "quiet"
    PERFORMANCE = "performance"
    PAUSE_BACKGROUND = "pause_background"


@dataclass(frozen=True, slots=True)
class ResourceSnapshot:
    snapshot_id: uuid.UUID
    captured_at_us: int
    ram_total_bytes: int | None
    ram_available_bytes: int | None
    disk_free_bytes: int
    cpu_load_fraction: float | None
    gpu_utilization_fraction: float | None
    vram_total_bytes: int | None
    vram_available_bytes: int | None
    model_loaded: bool | None
    degraded_metrics: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ResourcePolicy:
    mode: ResourceMode
    ram_headroom_bytes: int
    disk_headroom_bytes: int
    gpu_background_threshold: float
    updated_at_us: int
    updated_by_actor_id: uuid.UUID | None


@dataclass(frozen=True, slots=True)
class AdmissionDecision:
    admitted: bool
    reason: str | None
    retry_after_seconds: int


@dataclass(frozen=True, slots=True)
class InteractiveDemandLease:
    lease_id: uuid.UUID
    purpose: str
    acquired_at_us: int
    expires_at_us: int
    lease_seconds: int


class ResourceProbe(Protocol):
    def sample(self, paths: RuntimePaths) -> ResourceSnapshot:
        """Return best-effort local metrics; unavailable metrics stay None."""
        ...


class PortableResourceProbe:
    """Portable CPU/RAM/disk probe; GPU metrics intentionally degrade when unavailable."""

    def sample(self, paths: RuntimePaths) -> ResourceSnapshot:
        degraded: list[str] = []
        ram_total, ram_available = _memory_status()
        if ram_total is None or ram_available is None:
            degraded.append("ram")
        cpu_load = _cpu_load_fraction()
        if cpu_load is None:
            degraded.append("cpu")
        disk = shutil.disk_usage(paths.local_root)
        degraded.extend(("gpu_utilization", "vram"))
        return ResourceSnapshot(
            snapshot_id=new_uuid7(),
            captured_at_us=utc_now_us(),
            ram_total_bytes=ram_total,
            ram_available_bytes=ram_available,
            disk_free_bytes=disk.free,
            cpu_load_fraction=cpu_load,
            gpu_utilization_fraction=None,
            vram_total_bytes=None,
            vram_available_bytes=None,
            model_loaded=None,
            degraded_metrics=tuple(degraded),
        )


class StaticResourceProbe:
    """Deterministic probe for tests and explicit diagnostics."""

    def __init__(self, snapshot: ResourceSnapshot) -> None:
        self.snapshot = snapshot

    def sample(self, paths: RuntimePaths) -> ResourceSnapshot:
        del paths
        return replace(
            self.snapshot,
            snapshot_id=new_uuid7(),
            captured_at_us=utc_now_us(),
        )


class ResourceManager:
    """Persist resource mode and admit heavy durable jobs without changing semantics."""

    _RAM_MINIMUMS = {
        "source.process": 256 * 1024 * 1024,
        "source.analyze": 1024 * 1024 * 1024,
        "source.extract": 1024 * 1024 * 1024,
        "research.exhaustive": 1024 * 1024 * 1024,
        "embedding.rebuild": 512 * 1024 * 1024,
    }

    def __init__(
        self,
        *,
        database: SQLiteDatabase,
        paths: RuntimePaths,
        chat: ChatService,
        model_provider: ChatModelProvider,
        probe: ResourceProbe | None = None,
        interactive_lease_seconds: int = 360,
    ) -> None:
        validated_lease_seconds = _positive_int(
            interactive_lease_seconds,
            "Interactive demand lease duration",
        )
        self.database = database
        self.paths = paths
        self.chat = chat
        self.model_provider = model_provider
        self.probe = probe or PortableResourceProbe()
        self.interactive_lease_seconds = validated_lease_seconds

    @property
    def _interactive_lease_root(self) -> Path:
        return self.paths.state_root / "interactive-demand"

    def acquire_interactive_demand(
        self,
        *,
        purpose: str = "chat_generation",
        lease_seconds: int | None = None,
        now_us: int | None = None,
    ) -> InteractiveDemandLease:
        normalized_purpose = _canonical_text(
            purpose,
            "Interactive demand purpose",
        )
        duration = (
            self.interactive_lease_seconds
            if lease_seconds is None
            else _positive_int(
                lease_seconds,
                "Interactive demand lease duration",
            )
        )
        now = (
            utc_now_us()
            if now_us is None
            else _nonnegative_int(now_us, "Interactive demand timestamp")
        )
        expires_at_us = now + duration * 1_000_000
        lease_id = new_uuid7()

        root = self._interactive_lease_root
        root.mkdir(parents=True, exist_ok=True)
        self._cleanup_expired_interactive_leases(now_us=now)

        final_path = root / f"{lease_id}.json"
        staging_path = root / f".{lease_id}.partial"
        payload = json.dumps(
            {
                "lease_id": str(lease_id),
                "purpose": normalized_purpose,
                "owner_pid": os.getpid(),
                "acquired_at_us": now,
                "expires_at_us": expires_at_us,
                "lease_seconds": duration,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        try:
            with staging_path.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(staging_path, final_path)
            self._fsync_directory(root)
        finally:
            staging_path.unlink(missing_ok=True)

        return InteractiveDemandLease(
            lease_id=lease_id,
            purpose=normalized_purpose,
            acquired_at_us=now,
            expires_at_us=expires_at_us,
            lease_seconds=duration,
        )

    def renew_interactive_demand(
        self,
        lease: InteractiveDemandLease,
        *,
        now_us: int | None = None,
        force: bool = False,
    ) -> InteractiveDemandLease:
        validated_lease = _interactive_demand_lease(lease)
        validated_force = _exact_bool(force, "Interactive demand renewal force")
        now = (
            utc_now_us()
            if now_us is None
            else _nonnegative_int(now_us, "Interactive demand timestamp")
        )
        if now < validated_lease.acquired_at_us:
            raise ValueError(
                "Interactive demand renewal timestamp must not predate acquisition."
            )
        duration_us = validated_lease.lease_seconds * 1_000_000

        # Renewal is intentionally throttled. ChatGenerationService may call
        # this for every streamed token, but the durable lease file is only
        # rewritten after half of the current lease lifetime has elapsed.
        renew_at_us = (
            validated_lease.expires_at_us
            - max(1, duration_us // 2)
        )

        if not validated_force and now < renew_at_us:
            return validated_lease

        renewed = replace(
            validated_lease,
            expires_at_us=now + duration_us,
        )

        root = self._interactive_lease_root
        root.mkdir(
            parents=True,
            exist_ok=True,
        )

        final_path = (
            root
            / f"{validated_lease.lease_id}.json"
        )

        staging_path = (
            root
            / f".{validated_lease.lease_id}.partial"
        )

        payload = json.dumps(
            {
                "lease_id": str(
                    renewed.lease_id
                ),
                "purpose": (
                    renewed.purpose
                ),
                "owner_pid": os.getpid(),
                "acquired_at_us": (
                    renewed.acquired_at_us
                ),
                "renewed_at_us": now,
                "expires_at_us": (
                    renewed.expires_at_us
                ),
                "lease_seconds": (
                    renewed.lease_seconds
                ),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        staging_path.unlink(
            missing_ok=True
        )

        try:
            with staging_path.open(
                "xb"
            ) as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(
                    handle.fileno()
                )

            os.replace(
                staging_path,
                final_path,
            )

            self._fsync_directory(
                root
            )

        finally:
            staging_path.unlink(
                missing_ok=True
            )

        return renewed

    def release_interactive_demand(
        self,
        lease_id: uuid.UUID,
    ) -> None:
        validated_lease_id = _uuid_value(
            lease_id,
            "Interactive demand lease_id",
        )
        root = self._interactive_lease_root
        path = root / f"{validated_lease_id}.json"
        partial = root / f".{validated_lease_id}.partial"
        path.unlink(missing_ok=True)
        partial.unlink(missing_ok=True)

    @contextmanager
    def interactive_session(
        self,
        *,
        purpose: str = "chat_generation",
    ) -> Iterator[InteractiveDemandLease]:
        lease = self.acquire_interactive_demand(purpose=purpose)
        try:
            yield lease
        finally:
            self.release_interactive_demand(lease.lease_id)

    def interactive_demand_active(
        self,
        *,
        now_us: int | None = None,
    ) -> bool:
        now = (
            utc_now_us()
            if now_us is None
            else _nonnegative_int(now_us, "Interactive demand timestamp")
        )
        self._cleanup_expired_interactive_leases(now_us=now)
        root = self._interactive_lease_root
        if not root.is_dir():
            return False
        return any(root.glob("*.json"))

    def should_yield_to_interactive(
        self,
        job: JobRecord,
        *,
        now_us: int | None = None,
    ) -> bool:
        validated_now = _optional_nonnegative_int(
            now_us,
            "Interactive demand timestamp",
        )
        if job.priority <= JobPriority.INTERACTIVE:
            return False
        if not requires_provider_isolation(job.job_type):
            return False
        return self.interactive_demand_active(now_us=validated_now)

    def _cleanup_expired_interactive_leases(
        self,
        *,
        now_us: int,
    ) -> None:
        validated_now = _nonnegative_int(
            now_us,
            "Interactive demand timestamp",
        )
        root = self._interactive_lease_root
        if not root.is_dir():
            return

        fallback_ttl_us = self.interactive_lease_seconds * 1_000_000

        for path in root.glob("*.json"):
            expired = False
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                raw_expires = payload["expires_at_us"]
                expires_at_us = _nonnegative_int(
                    raw_expires,
                    "Interactive demand persisted expiry",
                )
                expired = expires_at_us <= validated_now
            except (KeyError, OSError, TypeError, ValueError):
                try:
                    modified_at_us = path.stat().st_mtime_ns // 1_000
                except OSError:
                    continue
                expired = modified_at_us + fallback_ttl_us <= validated_now

            if expired:
                path.unlink(missing_ok=True)

    @staticmethod
    def _fsync_directory(path: Path) -> None:
        try:
            descriptor = os.open(path, os.O_RDONLY)
        except OSError:
            return
        try:
            try:
                os.fsync(descriptor)
            except OSError:
                pass
        finally:
            os.close(descriptor)

    def policy(self) -> ResourcePolicy:
        row = self.database.connection.execute(
            "SELECT * FROM resource_policy WHERE singleton_id = 1"
        ).fetchone()
        if row is None:
            raise RuntimeError("ATHENA resource policy row is missing.")
        return ResourcePolicy(
            mode=ResourceMode(str(row["mode"])),
            ram_headroom_bytes=int(row["ram_headroom_bytes"]),
            disk_headroom_bytes=int(row["disk_headroom_bytes"]),
            gpu_background_threshold=float(row["gpu_background_threshold"]),
            updated_at_us=int(row["updated_at_us"]),
            updated_by_actor_id=(
                uuid_from_blob(bytes(row["updated_by_actor_id"]))
                if row["updated_by_actor_id"] is not None
                else None
            ),
        )

    def set_mode(self, mode: ResourceMode) -> ResourcePolicy:
        actor_id = self.chat.ensure_local_user()
        now_us = utc_now_us()
        with self.database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE resource_policy
                SET mode = ?, updated_at_us = ?, updated_by_actor_id = ?
                WHERE singleton_id = 1
                """,
                (mode.value, now_us, uuid_to_blob(actor_id)),
            )
        return self.policy()

    def snapshot(self, *, include_model: bool = True) -> ResourceSnapshot:
        validated_include_model = _exact_bool(
            include_model,
            "Resource snapshot include_model",
        )
        try:
            sampled = _resource_probe_snapshot(
                self.probe.sample(self.paths)
            )
        except Exception as exc:
            sampled = ResourceSnapshot(
                snapshot_id=new_uuid7(),
                captured_at_us=utc_now_us(),
                ram_total_bytes=None,
                ram_available_bytes=None,
                disk_free_bytes=0,
                cpu_load_fraction=None,
                gpu_utilization_fraction=None,
                vram_total_bytes=None,
                vram_available_bytes=None,
                model_loaded=None,
                degraded_metrics=("resource_probe", type(exc).__name__),
            )
        degraded = list(sampled.degraded_metrics)
        model_loaded = sampled.model_loaded
        if model_loaded is None:
            if validated_include_model:
                try:
                    models = self.model_provider.discover_models()
                except Exception:
                    degraded.append("model_availability")
                else:
                    model_loaded = any(
                        item.loaded for item in models if item.model_type == "llm"
                    )
            else:
                degraded.append("model_availability")

        snapshot = ResourceSnapshot(
            # Persisted samples always receive a fresh identity even when a
            # third-party/static probe accidentally reuses its own sample ID.
            snapshot_id=new_uuid7(),
            captured_at_us=utc_now_us(),
            ram_total_bytes=sampled.ram_total_bytes,
            ram_available_bytes=sampled.ram_available_bytes,
            disk_free_bytes=sampled.disk_free_bytes,
            cpu_load_fraction=sampled.cpu_load_fraction,
            gpu_utilization_fraction=sampled.gpu_utilization_fraction,
            vram_total_bytes=sampled.vram_total_bytes,
            vram_available_bytes=sampled.vram_available_bytes,
            model_loaded=model_loaded,
            degraded_metrics=tuple(sorted(set(degraded))),
        )
        self._persist_snapshot(snapshot)
        return snapshot

    def admit(self, job: JobRecord) -> AdmissionDecision:
        policy = self.policy()
        if job.priority is JobPriority.DATA_SAFETY:
            return AdmissionDecision(True, None, 0)
        if self.should_yield_to_interactive(job):
            return AdmissionDecision(
                False,
                "interactive chat demand has priority",
                5,
            )
        if (
            policy.mode is ResourceMode.PAUSE_BACKGROUND
            and job.priority >= JobPriority.BACKGROUND
        ):
            return AdmissionDecision(
                False,
                "background work paused by resource mode",
                60,
            )

        if (
            policy.mode is ResourceMode.QUIET
            and requires_provider_isolation(job.job_type)
            and job.priority >= JobPriority.NORMAL
        ):
            return AdmissionDecision(False, "quiet mode defers non-urgent GPU work", 60)

        snapshot = self.snapshot(include_model=False)
        if "resource_probe" in snapshot.degraded_metrics:
            return AdmissionDecision(False, "resource telemetry unavailable", 30)
        hard_ram = self._RAM_MINIMUMS.get(job.job_type, 256 * 1024 * 1024)
        ram_headroom = policy.ram_headroom_bytes
        disk_headroom = policy.disk_headroom_bytes
        if policy.mode is ResourceMode.QUIET:
            ram_headroom *= 2
            disk_headroom *= 2
        elif policy.mode is ResourceMode.PERFORMANCE:
            ram_headroom //= 2
            disk_headroom //= 2
        if (
            snapshot.ram_available_bytes is not None
            and snapshot.ram_available_bytes < ram_headroom + hard_ram
        ):
            return AdmissionDecision(False, "insufficient RAM headroom", 30)
        if snapshot.disk_free_bytes < disk_headroom:
            return AdmissionDecision(False, "insufficient disk headroom", 60)

        if requires_provider_isolation(job.job_type):
            if (
                snapshot.gpu_utilization_fraction is not None
                and snapshot.gpu_utilization_fraction
                >= policy.gpu_background_threshold
                and job.priority >= JobPriority.BACKGROUND
            ):
                return AdmissionDecision(False, "GPU busy with external work", 30)
            if (
                snapshot.vram_available_bytes is not None
                and snapshot.vram_available_bytes < 2 * 1024 * 1024 * 1024
                and job.priority >= JobPriority.BACKGROUND
            ):
                return AdmissionDecision(False, "insufficient VRAM headroom", 30)

        return AdmissionDecision(True, None, 0)

    def _persist_snapshot(self, snapshot: ResourceSnapshot) -> None:
        with self.database.write_transaction() as connection:
            connection.execute(
                """
                INSERT INTO resource_runtime_snapshots (
                    snapshot_id, captured_at_us, ram_total_bytes, ram_available_bytes,
                    disk_free_bytes, cpu_load_fraction, gpu_utilization_fraction,
                    vram_total_bytes, vram_available_bytes, model_loaded,
                    degraded_metrics_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid_to_blob(snapshot.snapshot_id),
                    snapshot.captured_at_us,
                    snapshot.ram_total_bytes,
                    snapshot.ram_available_bytes,
                    snapshot.disk_free_bytes,
                    snapshot.cpu_load_fraction,
                    snapshot.gpu_utilization_fraction,
                    snapshot.vram_total_bytes,
                    snapshot.vram_available_bytes,
                    (
                        int(snapshot.model_loaded)
                        if snapshot.model_loaded is not None
                        else None
                    ),
                    json.dumps(
                        list(snapshot.degraded_metrics),
                        separators=(",", ":"),
                    ),
                ),
            )
            connection.execute(
                """
                DELETE FROM resource_runtime_snapshots
                WHERE snapshot_id NOT IN (
                    SELECT snapshot_id
                    FROM resource_runtime_snapshots
                    ORDER BY captured_at_us DESC
                    LIMIT 256
                )
                """
            )


def _resource_probe_snapshot(value: object) -> ResourceSnapshot:
    if not isinstance(value, ResourceSnapshot):
        raise ValueError("Resource probe must return a ResourceSnapshot value.")

    ram_total = _optional_positive_int(
        value.ram_total_bytes,
        "Resource snapshot ram_total_bytes",
    )
    ram_available = _optional_nonnegative_int(
        value.ram_available_bytes,
        "Resource snapshot ram_available_bytes",
    )
    if ram_total is not None and ram_available is not None and ram_available > ram_total:
        raise ValueError(
            "Resource snapshot ram_available_bytes must not exceed ram_total_bytes."
        )

    vram_total = _optional_positive_int(
        value.vram_total_bytes,
        "Resource snapshot vram_total_bytes",
    )
    vram_available = _optional_nonnegative_int(
        value.vram_available_bytes,
        "Resource snapshot vram_available_bytes",
    )
    if vram_total is not None and vram_available is not None and vram_available > vram_total:
        raise ValueError(
            "Resource snapshot vram_available_bytes must not exceed vram_total_bytes."
        )

    if value.model_loaded is not None and not isinstance(value.model_loaded, bool):
        raise ValueError("Resource snapshot model_loaded must be null or boolean.")
    if not isinstance(value.degraded_metrics, tuple):
        raise ValueError("Resource snapshot degraded_metrics must be a tuple of text values.")
    degraded_metrics = tuple(
        _canonical_text(item, "Resource snapshot degraded metric")
        for item in value.degraded_metrics
    )

    return replace(
        value,
        ram_total_bytes=ram_total,
        ram_available_bytes=ram_available,
        disk_free_bytes=_nonnegative_int(
            value.disk_free_bytes,
            "Resource snapshot disk_free_bytes",
        ),
        cpu_load_fraction=_optional_fraction(
            value.cpu_load_fraction,
            "Resource snapshot cpu_load_fraction",
        ),
        gpu_utilization_fraction=_optional_fraction(
            value.gpu_utilization_fraction,
            "Resource snapshot gpu_utilization_fraction",
        ),
        vram_total_bytes=vram_total,
        vram_available_bytes=vram_available,
        degraded_metrics=degraded_metrics,
    )


def _interactive_demand_lease(value: object) -> InteractiveDemandLease:
    if not isinstance(value, InteractiveDemandLease):
        raise ValueError("Interactive demand lease must be an InteractiveDemandLease value.")
    _uuid_value(value.lease_id, "Interactive demand lease_id")
    _canonical_text(value.purpose, "Interactive demand purpose")
    acquired_at_us = _nonnegative_int(
        value.acquired_at_us,
        "Interactive demand acquired_at_us",
    )
    expires_at_us = _nonnegative_int(
        value.expires_at_us,
        "Interactive demand expires_at_us",
    )
    _positive_int(
        value.lease_seconds,
        "Interactive demand lease duration",
    )
    if expires_at_us <= acquired_at_us:
        raise ValueError(
            "Interactive demand expires_at_us must be greater than acquired_at_us."
        )
    return value


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be an integer >= 1.")
    return value


def _optional_positive_int(value: object | None, label: str) -> int | None:
    if value is None:
        return None
    return _positive_int(value, label)


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be an integer >= 0.")
    return value


def _optional_nonnegative_int(value: object | None, label: str) -> int | None:
    if value is None:
        return None
    return _nonnegative_int(value, label)


def _optional_fraction(value: object | None, label: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be null or a finite number in [0, 1].")
    result = float(value)
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        raise ValueError(f"{label} must be null or a finite number in [0, 1].")
    return result


def _canonical_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{label} must be canonical non-empty text.")
    return value


def _exact_bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a boolean.")
    return value


def _uuid_value(value: object, label: str) -> uuid.UUID:
    if not isinstance(value, uuid.UUID):
        raise ValueError(f"{label} must be a UUID value.")
    return value


def _memory_status() -> tuple[int | None, int | None]:
    if os.name == "nt":
        class MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        windll = getattr(ctypes, "windll", None)
        if windll is None:
            return None, None
        try:
            ok = windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
        except (AttributeError, OSError):
            return None, None
        if not ok:
            return None, None
        return int(status.ullTotalPhys), int(status.ullAvailPhys)

    sysconf = getattr(os, "sysconf", None)
    if not callable(sysconf):
        return None, None
    try:
        page_size = int(sysconf("SC_PAGE_SIZE"))
        total_pages = int(sysconf("SC_PHYS_PAGES"))
        available_pages = int(sysconf("SC_AVPHYS_PAGES"))
    except (OSError, TypeError, ValueError):
        return None, None
    return page_size * total_pages, page_size * available_pages


def _cpu_load_fraction() -> float | None:
    cpu_count = os.cpu_count()
    if not cpu_count:
        return None
    getloadavg = getattr(os, "getloadavg", None)
    if not callable(getloadavg):
        return None
    try:
        load = float(getloadavg()[0])
    except (OSError, TypeError, ValueError):
        return None
    return max(0.0, min(1.0, load / float(cpu_count)))
