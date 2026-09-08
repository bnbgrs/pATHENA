from __future__ import annotations

from athena.desktop.jobs_lifecycle import action_availability


def test_cancellation_requested_help_uses_product_language() -> None:
    availability = action_availability("cancel_requested")

    reasons = {
        availability.reason("pause"),
        availability.reason("resume"),
        availability.reason("wake"),
        availability.reason("cancel"),
    }

    assert reasons == {
        "Cancellation has already been requested and is waiting to complete."
    }
    visible = next(iter(reasons)).casefold()
    assert "worker" not in visible
    assert "acknowledgement" not in visible
    assert "persist" not in visible
    assert "lifecycle" not in visible
