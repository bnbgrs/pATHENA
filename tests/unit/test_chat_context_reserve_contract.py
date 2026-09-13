from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DIRECT_CHAT = REPO_ROOT / "src" / "athena" / "chat" / "direct.py"
GENERATION = REPO_ROOT / "src" / "athena" / "chat" / "generation.py"


def test_chat_preserves_adaptive_2048_output_reserve_contract() -> None:
    direct_source = DIRECT_CHAT.read_text(encoding="utf-8")
    generation_source = GENERATION.read_text(encoding="utf-8")

    assert "_DEFAULT_OUTPUT_RESERVE = 2048" in direct_source
    assert "output_reserve: int = _DEFAULT_OUTPUT_RESERVE" in direct_source
    assert (
        "available_output_tokens = context_limit - estimated_input_tokens - safety_margin"
        in direct_source
    )
    assert "return min(requested_output_reserve, available_output_tokens)" in direct_source
    assert (
        "output_reserve=(2048 if max_output_tokens is None else max_output_tokens)"
        in generation_source
    )
    assert (
        "output_reserve = 2048 if max_output_tokens is None else max_output_tokens"
        in generation_source
    )
