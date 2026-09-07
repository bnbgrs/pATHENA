from __future__ import annotations

import pytest

from athena.memory.learning_policy import (
    DEFAULT_PERSONAL_MEMORY_LEARNING_SETTING,
    PersonalMemoryLearningAction,
    PersonalMemoryLearningSetting,
    decide_personal_memory_learning,
)
from athena.memory.models import MemorySensitivity


def test_default_learning_setting_is_review_gated_suggest() -> None:
    decision = decide_personal_memory_learning(sensitivity=MemorySensitivity.NORMAL)

    assert DEFAULT_PERSONAL_MEMORY_LEARNING_SETTING is PersonalMemoryLearningSetting.SUGGEST
    assert decision.setting is PersonalMemoryLearningSetting.SUGGEST
    assert decision.action is PersonalMemoryLearningAction.PROPOSE


def test_learning_off_never_creates_automatic_memory_work() -> None:
    for sensitivity in MemorySensitivity:
        decision = decide_personal_memory_learning(
            setting=PersonalMemoryLearningSetting.OFF,
            sensitivity=sensitivity,
        )
        assert decision.action is PersonalMemoryLearningAction.IGNORE


def test_auto_non_sensitive_allows_only_normal_memory_to_auto_canonicalize() -> None:
    normal = decide_personal_memory_learning(
        setting=PersonalMemoryLearningSetting.AUTO_NON_SENSITIVE,
        sensitivity=MemorySensitivity.NORMAL,
    )
    sensitive = decide_personal_memory_learning(
        setting=PersonalMemoryLearningSetting.AUTO_NON_SENSITIVE,
        sensitivity=MemorySensitivity.SENSITIVE,
    )
    protected = decide_personal_memory_learning(
        setting=PersonalMemoryLearningSetting.AUTO_NON_SENSITIVE,
        sensitivity=MemorySensitivity.PROTECTED,
    )

    assert normal.action is PersonalMemoryLearningAction.AUTO_CANONICALIZE
    assert sensitive.action is PersonalMemoryLearningAction.REQUIRE_EXPLICIT_APPROVAL
    assert protected.action is PersonalMemoryLearningAction.REQUIRE_EXPLICIT_APPROVAL


def test_suggest_never_auto_canonicalizes_sensitive_or_protected_memory() -> None:
    for sensitivity in (MemorySensitivity.SENSITIVE, MemorySensitivity.PROTECTED):
        decision = decide_personal_memory_learning(
            setting=PersonalMemoryLearningSetting.SUGGEST,
            sensitivity=sensitivity,
        )
        assert decision.action is PersonalMemoryLearningAction.REQUIRE_EXPLICIT_APPROVAL


def test_learning_policy_rejects_untyped_runtime_values() -> None:
    with pytest.raises(TypeError, match="learning setting"):
        decide_personal_memory_learning(  # type: ignore[arg-type]
            setting="suggest",
            sensitivity=MemorySensitivity.NORMAL,
        )
    with pytest.raises(TypeError, match="sensitivity"):
        decide_personal_memory_learning(  # type: ignore[arg-type]
            setting=PersonalMemoryLearningSetting.SUGGEST,
            sensitivity="normal",
        )
