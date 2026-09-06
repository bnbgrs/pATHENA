from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_theme import PATHENA_SPECIALIZED_STYLESHEET


def test_workspace_action_controls_expose_explicit_keyboard_focus() -> None:
    selectors = (
        "QPushButton#detailsToggle:focus",
        "QPushButton#contextToggle:focus",
        "QPushButton#newChatButton:focus",
        "QPushButton#deleteChatButton:focus",
        "QPushButton#rememberMessageButton:focus",
        "QPushButton#addKnowledgeButton:focus",
        "QPushButton#groundButton:focus",
    )

    for selector in selectors:
        assert selector in PATHENA_SPECIALIZED_STYLESHEET

    focus_block = PATHENA_SPECIALIZED_STYLESHEET.split(
        "QPushButton#detailsToggle:focus,", maxsplit=1
    )[1].split("QPushButton#detailsToggle:checked,", maxsplit=1)[0]
    assert f"color: {PALETTE.text};" in focus_block
    assert f"background: {PALETTE.surface_hover};" in focus_block
    assert f"border-color: {PALETTE.accent};" in focus_block
