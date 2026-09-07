"""Deterministic policy for automatic ATHENA Personal-Memory learning."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from athena.memory.models import MemorySensitivity


class PersonalMemoryLearningSetting(str, Enum):
    """User-controlled global learning modes from the Beta specification."""

    OFF = "off"
    SUGGEST = "suggest"
    AUTO_NON_SENSITIVE = "auto_non_sensitive"


class PersonalMemoryLearningAction(str, Enum):
    """Policy outcome before any canonical Personal-Memory mutation."""

    IGNORE = "ignore"
    PROPOSE = "propose"
    AUTO_CANONICALIZE = "auto_canonicalize"
    REQUIRE_EXPLICIT_APPROVAL = "require_explicit_approval"


@dataclass(frozen=True, slots=True)
class PersonalMemoryLearningDecision:
    """Transport-neutral decision; it contains no inferred user content."""

    setting: PersonalMemoryLearningSetting
    sensitivity: MemorySensitivity
    action: PersonalMemoryLearningAction


DEFAULT_PERSONAL_MEMORY_LEARNING_SETTING = PersonalMemoryLearningSetting.SUGGEST


def decide_personal_memory_learning(
    *,
    setting: PersonalMemoryLearningSetting = DEFAULT_PERSONAL_MEMORY_LEARNING_SETTING,
    sensitivity: MemorySensitivity,
) -> PersonalMemoryLearningDecision:
    """Resolve the Beta learning-mode gate before proposal or persistence.

    ``off`` never creates an automatic proposal or canonical write. ``suggest``
    permits only a review-gated proposal. ``auto_non_sensitive`` may authorize
    automatic canonicalization only for NORMAL Memory. SENSITIVE and PROTECTED
    Memory always require an explicit user approval path regardless of mode.
    """
    if type(setting) is not PersonalMemoryLearningSetting:
        raise TypeError("Personal Memory learning setting must be PersonalMemoryLearningSetting.")
    if type(sensitivity) is not MemorySensitivity:
        raise TypeError("Personal Memory sensitivity must be MemorySensitivity.")

    if setting is PersonalMemoryLearningSetting.OFF:
        action = PersonalMemoryLearningAction.IGNORE
    elif sensitivity is not MemorySensitivity.NORMAL:
        action = PersonalMemoryLearningAction.REQUIRE_EXPLICIT_APPROVAL
    elif setting is PersonalMemoryLearningSetting.SUGGEST:
        action = PersonalMemoryLearningAction.PROPOSE
    else:
        action = PersonalMemoryLearningAction.AUTO_CANONICALIZE

    return PersonalMemoryLearningDecision(
        setting=setting,
        sensitivity=sensitivity,
        action=action,
    )
