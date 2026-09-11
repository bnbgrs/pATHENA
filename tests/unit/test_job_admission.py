from __future__ import annotations

from dataclasses import dataclass

import pytest

from athena.jobs.job_admission import (
    JobAdmissionError,
    RegistryBackedJobAdmission,
    UnboundPluginJobTypeError,
)
from athena.jobs.job_type_registry import JobTypeRegistry
from athena.jobs.models import JobPriority


@dataclass
class FakeService:
    BUILTIN_JOB_TYPES = frozenset({"source.process"})
    calls: list[dict[str, object]]

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return "builtin-record"


@dataclass
class FakePluginHandler:
    calls: list[dict[str, object]]

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return "plugin-record"


def test_constructor_requires_builtin_service_types_in_registry() -> None:
    with pytest.raises(JobAdmissionError, match="absent from registry"):
        RegistryBackedJobAdmission(
            registry=JobTypeRegistry(),
            builtin_service=FakeService([]),
        )


def test_builtin_admission_delegates_exact_arguments() -> None:
    registry = JobTypeRegistry(["source.process"])
    service = FakeService([])
    admission = RegistryBackedJobAdmission(
        registry=registry,
        builtin_service=service,
    )

    result = admission.create(
        job_type="source.process",
        priority=JobPriority.NORMAL,
        requested_scope={"source_id": "abc"},
        pinned_configuration={"model": "local"},
        next_run_at_us=10,
    )

    assert result == "builtin-record"
    assert service.calls == [
        {
            "job_type": "source.process",
            "priority": JobPriority.NORMAL,
            "requested_scope": {"source_id": "abc"},
            "pinned_configuration": {"model": "local"},
            "next_run_at_us": 10,
        }
    ]


def test_unregistered_type_fails_before_any_delegate() -> None:
    registry = JobTypeRegistry(["source.process"])
    service = FakeService([])
    admission = RegistryBackedJobAdmission(
        registry=registry,
        builtin_service=service,
    )

    with pytest.raises(JobAdmissionError, match="not registered"):
        admission.create(job_type="plugin.export")

    assert service.calls == []


def test_registered_plugin_without_handler_fails_closed() -> None:
    registry = JobTypeRegistry(["source.process"])
    registry.register_plugin("plugin.export", permission_granted=True)
    admission = RegistryBackedJobAdmission(
        registry=registry,
        builtin_service=FakeService([]),
    )

    with pytest.raises(UnboundPluginJobTypeError, match="no admission handler"):
        admission.create(job_type="plugin.export")


def test_plugin_handler_cannot_bind_before_permission_registration() -> None:
    registry = JobTypeRegistry(["source.process"])
    admission = RegistryBackedJobAdmission(
        registry=registry,
        builtin_service=FakeService([]),
    )

    with pytest.raises(JobAdmissionError, match="not registered"):
        admission.bind_plugin_handler("plugin.export", FakePluginHandler([]))


def test_builtin_type_cannot_be_shadowed_by_plugin_handler() -> None:
    registry = JobTypeRegistry(["source.process"])
    admission = RegistryBackedJobAdmission(
        registry=registry,
        builtin_service=FakeService([]),
    )

    with pytest.raises(JobAdmissionError, match="builtin"):
        admission.bind_plugin_handler("source.process", FakePluginHandler([]))


def test_plugin_handler_binding_is_unique() -> None:
    registry = JobTypeRegistry(["source.process"])
    registry.register_plugin("plugin.export", permission_granted=True)
    admission = RegistryBackedJobAdmission(
        registry=registry,
        builtin_service=FakeService([]),
    )
    admission.bind_plugin_handler("plugin.export", FakePluginHandler([]))

    with pytest.raises(JobAdmissionError, match="already"):
        admission.bind_plugin_handler("plugin.export", FakePluginHandler([]))


def test_registered_plugin_routes_only_to_explicit_handler() -> None:
    registry = JobTypeRegistry(["source.process"])
    registry.register_plugin("plugin.export", permission_granted=True)
    service = FakeService([])
    handler = FakePluginHandler([])
    admission = RegistryBackedJobAdmission(
        registry=registry,
        builtin_service=service,
    )
    admission.bind_plugin_handler("plugin.export", handler)

    result = admission.create(
        job_type="plugin.export",
        requested_scope={"entity_ref": "knowledge://item/1"},
    )

    assert result == "plugin-record"
    assert service.calls == []
    assert handler.calls == [
        {
            "job_type": "plugin.export",
            "priority": JobPriority.NORMAL,
            "requested_scope": {"entity_ref": "knowledge://item/1"},
            "pinned_configuration": None,
            "next_run_at_us": None,
        }
    ]
