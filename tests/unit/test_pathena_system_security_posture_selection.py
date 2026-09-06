from inspect import getsource

from athena.desktop.system_workspace import _PostureRow


def test_system_security_posture_values_are_keyboard_selectable() -> None:
    source = getsource(_PostureRow.__init__)

    assert 'self.value.setObjectName("settingsValue")' in source
    assert "Qt.TextInteractionFlag.TextSelectableByMouse" in source
    assert "Qt.TextInteractionFlag.TextSelectableByKeyboard" in source
