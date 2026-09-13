from __future__ import annotations

import pytest

from athena.jobs.job_type_registry import JobTypeRegistry


def test_builtin_job_types_are_registered_deterministically() -> None:
    registry = JobTypeRegistry(["source.process", "backup.create"])

    assert registry.contains("source.process")
    assert registry.contains("backup.create")
    assert registry.job_types == ("backup.create", "source.process")


def test_plugin_registration_requires_explicit_permission() -> None:
    registry = JobTypeRegistry()

    with pytest.raises(PermissionError, match="requires permission"):
        registry.register_plugin("plugin.example", permission_granted=False)

    assert not registry.contains("plugin.example")


@pytest.mark.parametrize("job_type", ["plain", ".missing_namespace", "missing_local."])
def test_plugin_registration_requires_namespace(job_type: str) -> None:
    registry = JobTypeRegistry()

    with pytest.raises(ValueError, match="namespaced"):
        registry.register_plugin(job_type, permission_granted=True)


def test_duplicate_registration_fails_closed() -> None:
    registry = JobTypeRegistry(["source.process"])

    with pytest.raises(ValueError, match="already registered"):
        registry.register_plugin("source.process", permission_granted=True)

    registry.register_plugin("plugin.example", permission_granted=True)
    with pytest.raises(ValueError, match="already registered"):
        registry.register_plugin("plugin.example", permission_granted=True)


@pytest.mark.parametrize("job_type", ["", " plugin.example", "plugin.example ", "plugin. bad"])
def test_invalid_job_type_is_rejected(job_type: str) -> None:
    registry = JobTypeRegistry()

    with pytest.raises(ValueError):
        registry.register_plugin(job_type, permission_granted=True)


def test_contains_fails_closed_for_invalid_input() -> None:
    registry = JobTypeRegistry(["source.process"])

    assert not registry.contains(None)
    assert not registry.contains(" source.process")
