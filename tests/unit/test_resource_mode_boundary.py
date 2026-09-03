from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.resources.manager import ResourceMode


@pytest.mark.parametrize(
    "invalid_mode",
    ("quiet", None, True, object()),
)
def test_set_mode_rejects_invalid_runtime_value_before_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    invalid_mode: object,
) -> None:
    app = AthenaApplication(
        settings=AthenaSettings(local_root=tmp_path / "invalid-mode-runtime")
    )
    app.start()
    try:
        original_policy = app.resources.policy()

        def fail_if_called() -> None:
            raise AssertionError("ensure_local_user must not run for invalid resource modes")

        monkeypatch.setattr(
            app.resources.chat,
            "ensure_local_user",
            fail_if_called,
        )

        with pytest.raises(TypeError, match="Resource mode must be a ResourceMode"):
            app.resources.set_mode(cast(ResourceMode, invalid_mode))

        assert app.resources.policy() == original_policy
    finally:
        app.stop()


@pytest.mark.parametrize("mode", tuple(ResourceMode))
def test_set_mode_accepts_all_resource_mode_values(
    tmp_path: Path,
    mode: ResourceMode,
) -> None:
    app = AthenaApplication(
        settings=AthenaSettings(local_root=tmp_path / f"valid-mode-{mode.value}")
    )
    app.start()
    try:
        policy = app.resources.set_mode(mode)
        assert policy.mode is mode
    finally:
        app.stop()
