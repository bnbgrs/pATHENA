from __future__ import annotations

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
        if not self.provider_id.strip():
            raise ValueError("provider_id must not be blank")
        if not self.provider_version.strip():
            raise ValueError("provider_version must not be blank")


@dataclass(frozen=True, slots=True)
class OCRResult:
    """Text recognized from one source payload."""

    text: str
    provider: ProviderIdentity
    confidence: float | None = None

    def __post_init__(self) -> None:
        _validate_confidence(self.confidence)


@dataclass(frozen=True, slots=True)
class SpeechTranscriptSegment:
    """One time-addressable speech transcript segment."""

    text: str
    start_time_ms: int
    end_time_ms: int
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("text must not be blank")
        if self.start_time_ms < 0:
            raise ValueError("start_time_ms must be >= 0")
        if self.end_time_ms <= self.start_time_ms:
            raise ValueError("end_time_ms must be greater than start_time_ms")
        _validate_confidence(self.confidence)


@dataclass(frozen=True, slots=True)
class SpeechToTextResult:
    """Provider transcript with segments suitable for source time anchors."""

    segments: tuple[SpeechTranscriptSegment, ...]
    provider: ProviderIdentity

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


def _validate_confidence(confidence: float | None) -> None:
    if confidence is not None and not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be between 0.0 and 1.0")
