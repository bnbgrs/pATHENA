from inspect import getsource

from athena.desktop.pathena_settings_runtime import SettingsRuntimeController
from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET


def test_settings_runtime_facts_are_keyboard_selectable_and_focus_visible() -> None:
    source = getsource(SettingsRuntimeController.__init__)

    assert "Qt.TextInteractionFlag.TextSelectableByMouse" in source
    assert "Qt.TextInteractionFlag.TextSelectableByKeyboard" in source
    for object_name in (
        "settingsProviderState",
        "settingsNetworkState",
        "settingsPersistenceState",
        "settingsRuntimeDetail",
    ):
        assert f'setObjectName("{object_name}")' in source
        assert f"QLabel#{object_name}:focus" in PATHENA_FOUNDATION_STYLESHEET
