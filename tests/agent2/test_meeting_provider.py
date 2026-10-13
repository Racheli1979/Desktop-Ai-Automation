from datetime import datetime

from agent2_meeting_agent.meeting import Meeting
from agent2_meeting_agent.meeting_provider import MeetingProvider


def create_provider(meetings):
    """
    Create a MeetingProvider using a controlled test source.
    """
    return MeetingProvider(
        meeting_source=lambda: meetings,
        upcoming_window_minutes=10,
    )


def test_upcoming_meeting_is_returned():
    current_time = datetime(
        2026,
        9,
        17,
        13,
        55,
    )

    meeting = Meeting(
        title="Project Review",
        start_time=datetime(
            2026,
            9,
            17,
            14,
            0,
        ),
        duration_minutes=60,
    )

    provider = create_provider([meeting])

    result = provider.get_upcoming_meetings(
        current_time
    )

    assert len(result) == 1
    assert isinstance(result[0], Meeting)
    assert result[0].title == "Project Review"


def test_meeting_that_already_started_is_ignored():
    current_time = datetime(
        2026,
        9,
        17,
        14,
        5,
    )

    meeting = Meeting(
        title="Project Review",
        start_time=datetime(
            2026,
            9,
            17,
            14,
            0,
        ),
        duration_minutes=60,
    )

    provider = create_provider([meeting])

    result = provider.get_upcoming_meetings(
        current_time
    )

    assert result == []


def test_meeting_starting_now_is_ignored():
    current_time = datetime(
        2026,
        9,
        17,
        14,
        0,
    )

    meeting = Meeting(
        title="Project Review",
        start_time=datetime(
            2026,
            9,
            17,
            14,
            0,
        ),
        duration_minutes=60,
    )

    provider = create_provider([meeting])

    result = provider.get_upcoming_meetings(
        current_time
    )

    assert result == []


def test_meeting_too_far_in_future_is_ignored():
    current_time = datetime(
        2026,
        9,
        17,
        13,
        55,
    )

    meeting = Meeting(
        title="Later Meeting",
        start_time=datetime(
            2026,
            9,
            17,
            14,
            30,
        ),
        duration_minutes=30,
    )

    provider = create_provider([meeting])

    result = provider.get_upcoming_meetings(
        current_time
    )

    assert result == []


def test_processed_meeting_is_not_returned_again():
    current_time = datetime(
        2026,
        9,
        17,
        13,
        55,
    )

    meeting = Meeting(
        title="Project Review",
        start_time=datetime(
            2026,
            9,
            17,
            14,
            0,
        ),
        duration_minutes=60,
    )

    provider = create_provider([meeting])

    first_result = provider.get_upcoming_meetings(
        current_time
    )

    assert len(first_result) == 1

    provider.mark_as_processed(meeting)

    second_result = provider.get_upcoming_meetings(
        current_time
    )

    assert second_result == []


def test_multiple_upcoming_meetings_are_returned():
    current_time = datetime(
        2026,
        9,
        17,
        13,
        55,
    )

    first_meeting = Meeting(
        title="Project Review",
        start_time=datetime(
            2026,
            9,
            17,
            14,
            0,
        ),
        duration_minutes=60,
    )

    second_meeting = Meeting(
        title="Team Sync",
        start_time=datetime(
            2026,
            9,
            17,
            14,
            5,
        ),
        duration_minutes=30,
    )

    provider = create_provider([
        first_meeting,
        second_meeting,
    ])

    result = provider.get_upcoming_meetings(
        current_time
    )

    assert len(result) == 2

    titles = {
        meeting.title
        for meeting in result
    }

    assert titles == {
        "Project Review",
        "Team Sync",
    }