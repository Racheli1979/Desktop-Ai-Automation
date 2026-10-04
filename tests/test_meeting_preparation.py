from unittest.mock import patch

from agent2_meeting_agent.desktop_controller import DesktopWindow
from agent2_meeting_agent.meeting import Meeting
from agent2_meeting_agent.meeting_classifier import MeetingDecision
from agent2_meeting_agent.meeting_preparation import (
    prepare_desktop_for_meeting,
)


def create_meeting(url="https://meet.google.com/example"):
    from datetime import datetime

    return Meeting(
        title="Project Review",
        start_time=datetime(2026, 10, 10, 14, 0),
        duration_minutes=60,
        participants=["Manager"],
        description="Important project review",
        meeting_url=url,
    )


def test_does_nothing_when_meeting_is_not_important():
    meeting = create_meeting()

    decision = MeetingDecision(
        important=False,
        reason="Routine meeting",
    )

    with (
        patch(
            "agent2_meeting_agent.meeting_preparation.close_open_windows"
        ) as mock_close,
        patch(
            "agent2_meeting_agent.meeting_preparation.open_meeting_url"
        ) as mock_open,
    ):
        result = prepare_desktop_for_meeting(
            meeting,
            decision,
        )

    assert result is False
    mock_close.assert_not_called()
    mock_open.assert_not_called()


def test_prepares_desktop_for_important_meeting():
    meeting = create_meeting()

    decision = MeetingDecision(
        important=True,
        reason="Important project decisions",
    )

    with (
        patch(
            "agent2_meeting_agent.meeting_preparation.close_open_windows",
            return_value=[],
        ) as mock_close,
        patch(
            "agent2_meeting_agent.meeting_preparation.open_meeting_url",
            return_value=True,
        ) as mock_open,
    ):
        result = prepare_desktop_for_meeting(
            meeting,
            decision,
        )

    assert result is True
    mock_close.assert_called_once()
    mock_open.assert_called_once_with(
        "https://meet.google.com/example"
    )


def test_fails_when_important_meeting_has_no_url():
    meeting = create_meeting(url=None)

    decision = MeetingDecision(
        important=True,
        reason="Important meeting",
    )

    with (
        patch(
            "agent2_meeting_agent.meeting_preparation.close_open_windows",
            return_value=[],
        ) as mock_close,
        patch(
            "agent2_meeting_agent.meeting_preparation.open_meeting_url"
        ) as mock_open,
    ):
        result = prepare_desktop_for_meeting(
            meeting,
            decision,
        )

    assert result is False
    mock_close.assert_called_once()
    mock_open.assert_not_called()


def test_continues_when_some_windows_fail_to_close():
    meeting = create_meeting()

    decision = MeetingDecision(
        important=True,
        reason="Important meeting",
    )

    with (
        patch(
            "agent2_meeting_agent.meeting_preparation.close_open_windows",
            return_value=[
                (
                    DesktopWindow(
                        handle=100,
                        title="Test Application",
                        process_id=1234,
                        process_name="test.exe",
                    ),
                    False,
                )
            ],
        ),
        patch(
            "agent2_meeting_agent.meeting_preparation.open_meeting_url",
            return_value=True,
        ) as mock_open,
    ):
        result = prepare_desktop_for_meeting(
            meeting,
            decision,
        )

    assert result is True
    mock_open.assert_called_once_with(
        "https://meet.google.com/example"
    )


def test_fails_when_meeting_cannot_be_opened():
    meeting = create_meeting()

    decision = MeetingDecision(
        important=True,
        reason="Important meeting",
    )

    with (
        patch(
            "agent2_meeting_agent.meeting_preparation.close_open_windows",
            return_value=[],
        ),
        patch(
            "agent2_meeting_agent.meeting_preparation.open_meeting_url",
            return_value=False,
        ),
    ):
        result = prepare_desktop_for_meeting(
            meeting,
            decision,
        )

    assert result is False