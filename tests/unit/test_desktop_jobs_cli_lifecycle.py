from __future__ import annotations

from dataclasses import dataclass

from athena.desktop import jobs_cli


@dataclass
class _StorageLifecycle:
    started: int = 0
    stopped: int = 0

    def start(self) -> None:
        self.started += 1

    def stop(self) -> None:
        self.stopped += 1


class _Jobs:
    def __init__(self, *, fail_list: bool = False) -> None:
        self.fail_list = fail_list

    def list(self, *, limit: int) -> tuple[object, ...]:
        assert limit == 150
        if self.fail_list:
            raise RuntimeError("jobs list failed")
        return ()


class _HelperApp:
    def __init__(self, *, fail_list: bool = False) -> None:
        self.storage_bootstrap = _StorageLifecycle()
        self.jobs = _Jobs(fail_list=fail_list)

    def start(self, **_kwargs: object) -> None:
        raise AssertionError("Jobs helper must not start the full Core lifecycle")

    def stop(self) -> None:
        raise AssertionError("Jobs helper must not stop the full Core lifecycle")


def test_jobs_cli_uses_storage_only_lifecycle(monkeypatch) -> None:
    app = _HelperApp()
    monkeypatch.setattr(jobs_cli, "AthenaApplication", lambda: app)

    result = jobs_cli.main(["list"])

    assert result == 0
    assert app.storage_bootstrap.started == 1
    assert app.storage_bootstrap.stopped == 1


def test_jobs_cli_stops_storage_after_command_failure(monkeypatch, capsys) -> None:
    app = _HelperApp(fail_list=True)
    monkeypatch.setattr(jobs_cli, "AthenaApplication", lambda: app)

    result = jobs_cli.main(["list"])

    assert result == 2
    assert app.storage_bootstrap.started == 1
    assert app.storage_bootstrap.stopped == 1
    assert "JOBS_ERROR RuntimeError: jobs list failed" in capsys.readouterr().err
