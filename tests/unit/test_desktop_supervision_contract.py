from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_APP = _REPO_ROOT / "src" / "athena" / "desktop" / "app.py"
_CORE_SUPERVISOR = _REPO_ROOT / "src" / "athena" / "desktop" / "supervisor.py"
_SCHEDULER_SUPERVISOR = (
    _REPO_ROOT / "src" / "athena" / "desktop" / "scheduler_supervisor.py"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_desktop_reuses_the_existing_qapplication() -> None:
    app = _text(_APP)

    assert "existing = QApplication.instance()" in app
    assert "if isinstance(existing, QApplication):\n        return existing" in app
    assert 'raise RuntimeError("pATHENA desktop requires QApplication ownership.")' in app


def test_desktop_owns_one_core_and_one_scheduler_supervisor() -> None:
    app = _text(_APP)

    assert app.count("DesktopCoreSupervisor(client=client, parent=app)") == 1
    assert app.count("DesktopJobSchedulerSupervisor(parent=app)") == 1
    assert "app.aboutToQuit.connect(scheduler_supervisor.stop)" in app
    assert "app.aboutToQuit.connect(supervisor.stop)" in app


def test_owned_supervisors_do_not_duplicate_active_children() -> None:
    core = _text(_CORE_SUPERVISOR)
    scheduler = _text(_SCHEDULER_SUPERVISOR)
    active_guard = "if self._stopping or self.child_active:\n            return"

    assert active_guard in core
    assert active_guard in scheduler
    assert "if self.child_active:\n            return" in core
    assert "if self.child_active:\n            return" in scheduler
