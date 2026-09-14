from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class ProviderUnavailableError(RuntimeError):
    """Raised when an OCR or speech-to-text provider cannot service a request."""


@dataclass(frozen=True, slots=True)
class ProviderIdentity:
    """Stable provider identity recorded with derived source representations."""

    provider_id: str
    provider_version: str

    def __post_init__(self) -> None:
        _validate_text(self.provider_id, "provider_id", allow_blank=False)
        _validate_text(
            self.provider_version,
            "provider_version",
            allow_blank=False,
        )


@dataclass(frozen=True, slots=True)
class OCRResult:
    """Text recognized from one source payload."""

    text: str
    provider: ProviderIdentity
    confidence: float | None = None

    def __post_init__(self) -> None:
        _validate_text(self.text, "text", allow_blank=True)
        _validate_provider(self.provider)
        _validate_confidence(self.confidence)


@dataclass(frozen=True, slots=True)
class SpeechTranscriptSegment:
    """One time-addressable speech transcript segment."""

    text: str
    start_time_ms: int
    end_time_ms: int
    confidence: float | None = None

    def __post_init__(self) -> None:
        _validate_text(self.text, "text", allow_blank=False)
        _validate_time_ms(self.start_time_ms, "start_time_ms")
        _validate_time_ms(self.end_time_ms, "end_time_ms")
        if self.end_time_ms <= self.start_time_ms:
            raise ValueError("end_time_ms must be greater than start_time_ms")
        _validate_confidence(self.confidence)


@dataclass(frozen=True, slots=True)
class SpeechToTextResult:
    """Provider transcript with segments suitable for source time anchors."""

    segments: tuple[SpeechTranscriptSegment, ...]
    provider: ProviderIdentity

    def __post_init__(self) -> None:
        if type(self.segments) is not tuple:
            raise TypeError("segments must be an immutable tuple")
        for segment in self.segments:
            if not isinstance(segment, SpeechTranscriptSegment):
                raise TypeError(
                    "segments must contain SpeechTranscriptSegment values"
                )
        _validate_provider(self.provider)

    @property
    def text(self) -> str:
        """Return the transcript in provider segment order."""

        return " ".join(segment.text for segment in self.segments)


class OCRProvider(Protocol):
    """Provider boundary for optical character recognition."""

    @property
    def identity(self) -> ProviderIdentity:
        """Return the stable provider identity used for provenance."""

        ...

    def recognize(
        self,
        source_path: Path,
        *,
        media_type: str | None = None,
    ) -> OCRResult:
        """Recognize verified local source bytes without mutating them."""

        ...


class SpeechToTextProvider(Protocol):
    """Provider boundary for time-addressable speech transcription."""

    @property
    def identity(self) -> ProviderIdentity:
        """Return the stable provider identity used for provenance."""

        ...

    def transcribe(
        self,
        source_path: Path,
        *,
        media_type: str | None = None,
    ) -> SpeechToTextResult:
        """Transcribe verified local source bytes without mutating them."""

        ...


def _validate_text(value: str, field_name: str, *, allow_blank: bool) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    if not allow_blank and not value.strip():
        raise ValueError(f"{field_name} must not be blank")


def _validate_provider(provider: ProviderIdentity) -> None:
    if not isinstance(provider, ProviderIdentity):
        raise TypeError("provider must be a ProviderIdentity")


def _validate_confidence(confidence: float | None) -> None:
    if confidence is None:
        return
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise TypeError("confidence must be a real number or None")
    numeric_confidence = float(confidence)
    if not math.isfinite(numeric_confidence) or not 0.0 <= numeric_confidence <= 1.0:
        raise ValueError("confidence must be between 0.0 and 1.0")


def _validate_time_ms(value: int, field_name: str) -> None:
    if type(value) is not int:
        raise TypeError(f"{field_name} must be an integer")
    if value < 0:
        raise ValueError(f"{field_name} must be >= 0")
