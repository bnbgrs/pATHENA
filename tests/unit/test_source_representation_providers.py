from __future__ import annotations

from pathlib import Path

import pytest

from athena.source.representation_providers import (
    OCRProvider,
    OCRResult,
    ProviderIdentity,
    ProviderUnavailableError,
    SpeechToTextProvider,
    SpeechToTextResult,
    SpeechTranscriptSegment,
)


def test_provider_identity_rejects_blank_values() -> None:
    with pytest.raises(ValueError, match="provider_id"):
        ProviderIdentity(provider_id=" ", provider_version="1")

    with pytest.raises(ValueError, match="provider_version"):
        ProviderIdentity(provider_id="provider", provider_version="\t")


def test_ocr_result_accepts_empty_text_and_bounded_confidence() -> None:
    provider = ProviderIdentity(provider_id="ocr", provider_version="1")

    assert OCRResult(text="", provider=provider).text == ""
    assert OCRResult(text="text", provider=provider, confidence=0.0).confidence == 0.0
    assert OCRResult(text="text", provider=provider, confidence=1.0).confidence == 1.0


@pytest.mark.parametrize("confidence", [-0.01, 1.01, float("nan"), float("inf")])
def test_ocr_result_rejects_invalid_confidence(confidence: float) -> None:
    provider = ProviderIdentity(provider_id="ocr", provider_version="1")

    with pytest.raises(ValueError, match="confidence"):
        OCRResult(text="text", provider=provider, confidence=confidence)


def test_speech_segment_validates_text_and_time_range() -> None:
    with pytest.raises(ValueError, match="text"):
        SpeechTranscriptSegment(text=" ", start_time_ms=0, end_time_ms=1)

    with pytest.raises(ValueError, match="start_time_ms"):
        SpeechTranscriptSegment(text="text", start_time_ms=-1, end_time_ms=1)

    with pytest.raises(ValueError, match="end_time_ms"):
        SpeechTranscriptSegment(text="text", start_time_ms=10, end_time_ms=10)

    with pytest.raises(ValueError, match="end_time_ms"):
        SpeechTranscriptSegment(text="text", start_time_ms=10, end_time_ms=9)


@pytest.mark.parametrize("confidence", [-0.01, 1.01, float("nan"), float("-inf")])
def test_speech_segment_rejects_invalid_confidence(confidence: float) -> None:
    with pytest.raises(ValueError, match="confidence"):
        SpeechTranscriptSegment(
            text="text",
            start_time_ms=0,
            end_time_ms=1,
            confidence=confidence,
        )


def test_speech_result_preserves_provider_order_and_allows_overlap() -> None:
    provider = ProviderIdentity(provider_id="stt", provider_version="2")
    first = SpeechTranscriptSegment(
        text="hello",
        start_time_ms=0,
        end_time_ms=800,
        confidence=0.9,
    )
    second = SpeechTranscriptSegment(
        text="world",
        start_time_ms=500,
        end_time_ms=1200,
        confidence=0.8,
    )

    result = SpeechToTextResult(segments=(first, second), provider=provider)

    assert result.text == "hello world"
    assert result.segments == (first, second)
    assert result.provider is provider


def test_provider_unavailable_error_is_runtime_error() -> None:
    error = ProviderUnavailableError("offline")

    assert isinstance(error, RuntimeError)


class _OCRProvider:
    @property
    def identity(self) -> ProviderIdentity:
        return ProviderIdentity(provider_id="fake-ocr", provider_version="1")

    def recognize(
        self,
        source_path: Path,
        *,
        media_type: str | None = None,
    ) -> OCRResult:
        del source_path, media_type
        return OCRResult(text="recognized", provider=self.identity)


class _SpeechToTextProvider:
    @property
    def identity(self) -> ProviderIdentity:
        return ProviderIdentity(provider_id="fake-stt", provider_version="1")

    def transcribe(
        self,
        source_path: Path,
        *,
        media_type: str | None = None,
    ) -> SpeechToTextResult:
        del source_path, media_type
        return SpeechToTextResult(segments=(), provider=self.identity)


def _accept_ocr_provider(provider: OCRProvider) -> OCRProvider:
    return provider


def _accept_speech_provider(provider: SpeechToTextProvider) -> SpeechToTextProvider:
    return provider


def test_protocols_accept_structural_provider_implementations(tmp_path: Path) -> None:
    ocr_provider = _accept_ocr_provider(_OCRProvider())
    speech_provider = _accept_speech_provider(_SpeechToTextProvider())
    source_path = tmp_path / "source.bin"
    source_path.write_bytes(b"source")

    assert ocr_provider.recognize(source_path).text == "recognized"
    assert speech_provider.transcribe(source_path).segments == ()
