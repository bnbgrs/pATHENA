from __future__ import annotations

from athena.chat.unified import UnifiedLocalChatService as DurableUnifiedLocalChatService
from athena.chat.unified_resumable import UnifiedLocalChatService as ResumableUnifiedLocalChatService
from athena.core import application


def test_core_wires_pre_user_resumable_unified_service() -> None:
    assert application.UnifiedLocalChatService is ResumableUnifiedLocalChatService
    assert issubclass(ResumableUnifiedLocalChatService, DurableUnifiedLocalChatService)
