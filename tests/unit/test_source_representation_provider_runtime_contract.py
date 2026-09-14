from __future__ import annotations

from typing import cast

import pytest

from athena.source.representation_providers import (
    OCRResult,
    ProviderIdentity,
    SpeechToTextResult,
    SpeechTranscriptSegment,
)


def _provider() -> ProviderIdentity:
    return ProviderIdentity(provider_id="provider", provider_version="1")


@pytest.mark.parametrize("field_name", ["provider_id", "provider_version"])
def test_provider_identity_rejects_non_string_runtime_values(
    field_name: str,
) -> None:
    kwargs = {
        "provider_id": "provider",
        "provider_version": "1",
    }
    kwargs[field_name] = cast(str, object())

    with pytest.raises(TypeError, match=field_name):
        ProviderIdentity(**kwargs)


def test_ocr_result_rejects_non_string_text() -> None:
    with pytest.raises(TypeError, match="text"):
        OCRResult(
            text=cast(str, b"recognized"),
            provider=_provider(),
        )


def test_ocr_result_rejects_invalid_provider_runtime_value() -> None:
    with pytest.raises(TypeError, match="provider"):
        OCRResult(
            text="recognized",
            provider=cast(ProviderIdentity, object()),
        )


def test_speech_segment_rejects_non_string_text() -> None:
    with pytest.raises(TypeError, match="text"):
        SpeechTranscriptSegment(
            text=cast(str, b"spoken"),
            start_time_ms=0,
            end_time_ms=1,
        )


def test_speech_result_requires_immutable_tuple_segments() -> None:
    segment = SpeechTranscriptSegment(
        text="spoken",
        start_time_ms=0,
        end_time_ms=1,
    )

    with pytest.raises(TypeError, match="immutable tuple"):
        SpeechToTextResult(
            segments=cast(tuple[SpeechTranscriptSegment, ...], [segment]),
            provider=_provider(),
        )


def test_speech_result_rejects_invalid_segment_runtime_value() -> None:
    with pytest.raises(TypeError, match="SpeechTranscriptSegment"):
        SpeechToTextResult(
            segments=(cast(SpeechTranscriptSegment, object()),),
            provider=_provider(),
        )


def test_speech_result_rejects_invalid_provider_runtime_value() -> None:
    with pytest.raises(TypeError, match="provider"):
        SpeechToTextResult(
            segments=(),
            provider=cast(ProviderIdentity, object()),
        )
