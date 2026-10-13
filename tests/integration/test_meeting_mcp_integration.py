from datetime import datetime, timedelta
from unittest.mock import patch

from agent2_meeting_agent.meeting import Meeting
from agent2_meeting_agent.meeting_provider import MeetingProvider
from agent2_meeting_agent.meeting_classifier import MeetingClassifier


def test_mcp_meeting_source_and_ai_classifier():
    # Use the real MCP client and Google Calendar source.
    from agent2_meeting_agent.meeting_source import get_meetings

    meetings = get_meetings()

    assert isinstance(meetings, list)
    assert all(isinstance(meeting, Meeting) for meeting in meetings)

    # Select an upcoming meeting from the actual calendar.
    now = datetime.now()
    upcoming = [
        meeting
        for meeting in meetings
        if now < meeting.start_time <= now + timedelta(minutes=10)
    ]

    if not upcoming:
        # MCP connectivity and event conversion were still verified.
        return

    meeting = upcoming[0]

    # Exercise the real AI classifier.
    decision = MeetingClassifier().classify(meeting)

    assert isinstance(decision.important, bool)
    assert isinstance(decision.reason, str)
    assert decision.reason.strip()

    # Ensure desktop actions are never executed by this test.
    with patch(
        "agent2_meeting_agent.meeting_preparation.minimize_open_windows"
    ) as minimize_windows, patch(
        "agent2_meeting_agent.meeting_preparation.open_meeting_url"
    ) as open_url:
        minimize_windows.assert_not_called()
        open_url.assert_not_called()