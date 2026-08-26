"""Truthful presentation model for the pATHENA SYSTEM workspace."""

from __future__ import annotations

from dataclasses import dataclass

from athena.api.contracts import StorageHealthResponse
from athena.desktop.api_controller import DesktopApiSnapshot


@dataclass(frozen=True, slots=True)
class RuntimeFact:
    """One status value whose provenance is an existing desktop API probe."""

    value: str
    state: str


@dataclass(frozen=True, slots=True)
class SystemRuntimeOverview:
    """Read-only system facts derived without synthesising telemetry."""

    core: RuntimeFact
    provider: RuntimeFact
    api: RuntimeFact
    models: RuntimeFact
    loaded_models: RuntimeFact
    chats: RuntimeFact
    storage: RuntimeFact
    network: RuntimeFact
    background: RuntimeFact
    loopback: RuntimeFact
    local_processing: RuntimeFact
    encrypted_at_rest: RuntimeFact
    tor: RuntimeFact
    detail: str
    state: str


def project_system_runtime(snapshot: DesktopApiSnapshot) -> SystemRuntimeOverview:
    """Project one coherent API snapshot into explicit operational states."""

    core_value = _display(snapshot.health.core_status)
    core_state = _health_state(snapshot.health.core_status)
    provider = snapshot.provider
    model_freshness = snapshot.resolved_model_freshness
    chat_freshness = snapshot.resolved_chat_freshness

    if provider is None:
        provider_fact = RuntimeFact("Unavailable", "unavailable")
        network_fact = RuntimeFact("Provider unavailable", "unavailable")
        local_processing_fact = RuntimeFact("Unavailable", "unavailable")
    elif model_freshness == "stale":
        provider_fact = RuntimeFact(f"{_display(provider.status)} · stale", "stale")
        network_fact = RuntimeFact("Provider state stale", "stale")
        local_processing_fact = RuntimeFact(
            f"{_display(provider.provider)} · stale",
            "stale",
        )
    else:
        provider_state = _health_state(provider.status)
        provider_fact = RuntimeFact(_display(provider.status), provider_state)
        network_fact = RuntimeFact(
            "Provider reachable" if provider_state == "success" else "Provider degraded",
            provider_state,
        )
        local_processing_fact = RuntimeFact(
            _display(provider.provider),
            provider_state,
        )

    models = _count_fact(len(snapshot.models), model_freshness)
    loaded = _count_fact(
        sum(model.loaded for model in snapshot.models),
        model_freshness,
    )
    chats = _count_fact(len(snapshot.chats), chat_freshness)

    storage = _snapshot_storage(snapshot)
    storage_error = _snapshot_storage_error(snapshot)
    storage_fact = _storage_fact(storage)

    details: list[str] = []
    if snapshot.health.detail:
        details.append(snapshot.health.detail)
    if provider is not None and provider.detail:
        details.append(provider.detail)
    if snapshot.model_error:
        details.append("Model discovery: " + snapshot.model_error)
    if snapshot.chat_error:
        details.append("Chat discovery: " + snapshot.chat_error)
    if storage is None:
        details.append(
            "Storage telemetry: "
            + (
                storage_error
                or "unavailable — the desktop API snapshot exposes no storage probe."
            )
        )
    elif storage.detail:
        details.append("Storage: " + storage.detail)
    else:
        details.append("Storage: " + _storage_summary(storage))
    details.extend(
        (
            "Background activity history: unavailable — the desktop API snapshot "
            "exposes no event feed.",
            "Security posture: loopback binding, encryption-at-rest and Tor state "
            "are not exposed by this snapshot.",
        )
    )
    if len(details) == 3:
        details.insert(0, "Core, provider and storage snapshot data is current.")

    states = [
        core_state,
        provider_fact.state,
        models.state,
        chats.state,
    ]
    if storage is not None:
        states.append(storage_fact.state)
    overall = (
        "error"
        if "error" in states
        else "stale"
        if "stale" in states
        else "unavailable"
        if "unavailable" in states
        else "success"
    )
    unavailable = RuntimeFact("Unavailable", "unavailable")
    return SystemRuntimeOverview(
        core=RuntimeFact(core_value, core_state),
        provider=provider_fact,
        api=RuntimeFact(snapshot.health.api_version.upper(), core_state),
        models=models,
        loaded_models=loaded,
        chats=chats,
        storage=storage_fact,
        network=network_fact,
        background=unavailable,
        loopback=unavailable,
        local_processing=local_processing_fact,
        encrypted_at_rest=unavailable,
        tor=unavailable,
        detail="\n".join(details),
        state=overall,
    )


def disconnected_system_runtime(message: str) -> SystemRuntimeOverview:
    """Represent a failed Core connection without retaining old live values."""

    unavailable = RuntimeFact("Unavailable", "unavailable")
    return SystemRuntimeOverview(
        core=RuntimeFact("Disconnected", "error"),
        provider=unavailable,
        api=unavailable,
        models=unavailable,
        loaded_models=unavailable,
        chats=unavailable,
        storage=unavailable,
        network=RuntimeFact("Core unreachable", "error"),
        background=unavailable,
        loopback=unavailable,
        local_processing=unavailable,
        encrypted_at_rest=unavailable,
        tor=unavailable,
        detail=(
            f"{message}\n"
            "Storage telemetry, background activity and security posture are unavailable "
            "while the Core snapshot cannot be read."
        ),
        state="error",
    )


def _snapshot_storage(snapshot: DesktopApiSnapshot) -> StorageHealthResponse | None:
    storage = getattr(snapshot, "storage", None)
    return storage if isinstance(storage, StorageHealthResponse) else None


def _snapshot_storage_error(snapshot: DesktopApiSnapshot) -> str | None:
    error = getattr(snapshot, "storage_error", None)
    return error if isinstance(error, str) and error else None


def _storage_fact(storage: StorageHealthResponse | None) -> RuntimeFact:
    if storage is None:
        return RuntimeFact("Unavailable", "unavailable")
    state = _health_state(storage.status)
    if storage.status == "available":
        return RuntimeFact(_storage_summary(storage), state)
    return RuntimeFact(_display(storage.status), state)


def _storage_summary(storage: StorageHealthResponse) -> str:
    if not storage.database_open:
        return "Database closed"
    sizes: list[str] = []
    if storage.database_size_bytes is not None:
        sizes.append(f"DB {_format_bytes(storage.database_size_bytes)}")
    if storage.wal_size_bytes is not None:
        sizes.append(f"WAL {_format_bytes(storage.wal_size_bytes)}")
    return "Available" if not sizes else "Available · " + " · ".join(sizes)


def _format_bytes(value: int) -> str:
    amount = float(value)
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    unit = units[0]
    for candidate in units:
        unit = candidate
        if amount < 1024.0 or candidate == units[-1]:
            break
        amount /= 1024.0
    if unit == "B":
        return f"{int(amount)} {unit}"
    return f"{amount:.1f} {unit}"


def _count_fact(count: int, freshness: str) -> RuntimeFact:
    if freshness == "fresh":
        return RuntimeFact(str(count), "success")
    if freshness == "stale":
        return RuntimeFact(f"{count} · stale", "stale")
    return RuntimeFact("Unavailable", "unavailable")


def _display(value: str) -> str:
    return value.replace("_", " ").strip().capitalize() or "Unavailable"


def _health_state(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in {"ok", "ready", "healthy", "available", "connected"}:
        return "success"
    if normalized in {"unknown", "unavailable", "disconnected"}:
        return "unavailable"
    return "error"
