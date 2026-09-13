from athena.desktop.pathena_design_tokens import TYPE
from athena.desktop.pathena_startup_experience_2900 import _STARTUP_STYLESHEET
from athena.desktop.pathena_theme import _build_specialized_stylesheet


def test_startup_stylesheet_preserves_canonical_page_title_hierarchy() -> None:
    """Late startup styling must not collapse the canonical workspace title scale."""
    canonical_stylesheet = _build_specialized_stylesheet()

    assert "QLabel#pageTitle" not in _STARTUP_STYLESHEET
    assert f"font-size: {TYPE.title_px}px;" in canonical_stylesheet
