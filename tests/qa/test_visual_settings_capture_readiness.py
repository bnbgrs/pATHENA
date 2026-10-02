from scripts.render_pathena_ui_snapshot_sequential import _settings_capture_ready


def _ready(**overrides: object) -> tuple[bool, str]:
    values: dict[str, object] = {
        "shell_status": "Model error",
        "provider_text": "lm_studio · last known unavailable",
        "network_text": "Local Core · connected",
        "news_text": "News disabled · daily 07:00 · Europe/Berlin",
        "snapshot_received": True,
        "news_requested": True,
        "news_busy": False,
    }
    values.update(overrides)
    return _settings_capture_ready(**values)  # type: ignore[arg-type]


def test_settings_visual_capture_accepts_settled_runtime_state() -> None:
    ready, reason = _ready()

    assert ready is True
    assert reason == "stable runtime-backed Settings state"


def test_settings_visual_capture_rejects_connecting_shell() -> None:
    ready, reason = _ready(shell_status="Connecting…")

    assert ready is False
    assert reason == "shell status is still transient"


def test_settings_visual_capture_requires_real_core_snapshot() -> None:
    ready, reason = _ready(snapshot_received=False)

    assert ready is False
    assert reason == "waiting for first Core snapshot"


def test_settings_visual_capture_rejects_initial_runtime_labels() -> None:
    assert _ready(provider_text="Model service · waiting")[0] is False
    assert _ready(network_text="Local service · waiting")[0] is False


def test_settings_visual_capture_waits_for_news_profile_terminal_state() -> None:
    assert _ready(news_requested=False)[0] is False
    assert _ready(news_busy=True)[0] is False
    assert _ready(news_text="News schedule · waiting for local service")[0] is False
    assert _ready(news_text="News schedule · loading…")[0] is False
    assert _ready(news_text="News schedule · saving…")[0] is False


def test_settings_visual_capture_accepts_terminal_news_failure() -> None:
    ready, _reason = _ready(
        news_text="News schedule unavailable · local Core rejected request"
    )

    assert ready is True
