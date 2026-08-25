from __future__ import annotations

from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET


def test_meaningful_shared_metadata_uses_subtle_text_tier() -> None:
    metadata_block = PATHENA_FOUNDATION_STYLESHEET.split(
        "QLabel#localStatus,", maxsplit=1
    )[1].split("QFrame#rule", maxsplit=1)[0]

    assert "QLabel#networkState" in metadata_block
    assert "QLabel#keyboardHint" in metadata_block
    assert "QLabel#breadcrumb" in metadata_block
    assert "QLabel#sessionLabel" in metadata_block
    assert "QLabel#settingsLabel" in metadata_block
    assert "QLabel#inspectorEvidenceMeta" in metadata_block
    assert "QLabel#inspectorActivityItem" in metadata_block
    assert f"color: {PALETTE.text_subtle};" in metadata_block
    assert f"color: {PALETTE.text_quiet};" not in metadata_block


def test_reference_inspector_uses_real_evidence_card_hierarchy() -> None:
    inspector_block = PATHENA_FOUNDATION_STYLESHEET.split(
        "QFrame#groundedInspectorPanel", maxsplit=1
    )[1].split("QFrame#pallasVisualPlaceholder", maxsplit=1)[0]

    assert "QLabel#inspectorSectionTitle" in inspector_block
    assert "QFrame#inspectorEvidenceCard" in inspector_block
    assert 'QFrame#inspectorEvidenceCard[cited="true"]' in inspector_block
    assert "QLabel#inspectorEvidenceTitle" in inspector_block
    assert "QLabel#inspectorActivityItem" in inspector_block
    assert f"border-left: 2px solid {PALETTE.accent};" in inspector_block


def test_composer_is_prominent_blue_reference_action_area() -> None:
    composer_block = PATHENA_FOUNDATION_STYLESHEET.split(
        "QFrame#composer", maxsplit=1
    )[1].split("QPushButton {{", maxsplit=1)[0]
    send_block = PATHENA_FOUNDATION_STYLESHEET.split(
        "QPushButton#sendButton,", maxsplit=1
    )[1].split("QPushButton#sendButton:hover", maxsplit=1)[0]

    assert "QLineEdit#promptInput" in composer_block
    assert "QPushButton#groundButton" in composer_block
    assert f"background: {PALETTE.surface_raised};" in composer_block
    assert f"background: {PALETTE.accent};" in send_block
    assert "min-width: 44px;" in send_block
    assert "border-radius: 22px;" in send_block


def test_disabled_and_decorative_states_remain_quiet() -> None:
    disabled_block = PATHENA_FOUNDATION_STYLESHEET.split(
        "QPushButton:disabled,", maxsplit=1
    )[1].split("QLineEdit,", maxsplit=1)[0]
    scrollbar_hover_block = PATHENA_FOUNDATION_STYLESHEET.split(
        "QScrollBar::handle:vertical:hover", maxsplit=1
    )[1]

    assert f"color: {PALETTE.text_quiet};" in disabled_block
    assert f"background: {PALETTE.text_quiet};" in scrollbar_hover_block
