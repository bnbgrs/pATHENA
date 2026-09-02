from __future__ import annotations

import uuid

from athena.chat.grounded_reconciliation import (
    GroundedReconciliationState,
    GroundedSendReconciler,
)
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.common.ids import uuid_to_blob
from athena.storage.database import SQLiteDatabase


def test_reconciliation_classifies_operation_fingerprint_corruption_as_conflict(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        operation_id = uuid.uuid4()
        fingerprint = build_chat_request_fingerprint(
            mode=ChatSendMode.GROUNDED,
            chat_id=chat_id,
            content="hello",
            requested_model_id="primary",
            requested_embedding_model_id=None,
            effective_context_limit=4096,
            max_output_tokens=1024,
            temperature=0.3,
            reasoning_mode="off",
            retrieval_configuration={},
        )
        GroundedUserTurnRepository(database).commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=fingerprint,
        )
        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE chat_send_operations
                SET request_fingerprint_sha256 = ?
                WHERE operation_id = ?
                """,
                ("0" * 64, uuid_to_blob(operation_id)),
            )

        status = GroundedSendReconciler(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is GroundedReconciliationState.CONFLICT
        assert status.receipt is None
    finally:
        database.stop()
