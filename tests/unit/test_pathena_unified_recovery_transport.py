from __future__ import annotations

from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedRecoveryStatus
from athena.chat.send_identity import SendOperationStateError
from athena.chat.unified_resumable import (
    UnifiedGroundedTransportRecoveryRequiredError,
)
from athena.common.ids import new_uuid7


def test_post_user_recovery_error_keeps_domain_status_and_api_classification() -> None:
    status = GroundedRecoveryStatus(
        operation_id=new_uuid7(),
        chat_id=new_uuid7(),
        state=GroundedRecoveryState.AMBIGUOUS,
        receipt=None,
        processing_run_id=new_uuid7(),
    )

    error = UnifiedGroundedTransportRecoveryRequiredError(status)

    assert isinstance(error, SendOperationStateError)
    assert error.recovery_status is status
    assert error.status is status
    assert error.status.state is GroundedRecoveryState.AMBIGUOUS
