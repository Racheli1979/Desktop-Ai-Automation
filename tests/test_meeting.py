from datetime import datetime

import pytest

from agent2_meeting_agent.meeting import Meeting


def test_create_valid_meeting():
    meeting = Meeting(
        title="Important Project Meeting",
        start_time=datetime(2026, 9, 17, 14, 0),
        duration_minutes=60,
        participants=[
            "Manager",
            "Tech Lead",
        ],
        description="Discuss important project decisions",
        meeting_url="https://meet.google.com/example",
    )

    meeting.validate()

    assert meeting.title == "Important Project Meeting"
    assert meeting.start_time == datetime(
        2026, 9, 17, 14, 0
    )
    assert meeting.duration_minutes == 60
    assert meeting.participants == [
        "Manager",
        "Tech Lead",
    ]
    assert meeting.description == (
        "Discuss important project decisions"
    )
    assert meeting.meeting_url == (
        "https://meet.google.com/example"
    )


def test_meeting_end_time():
    meeting = Meeting(
        title="Team Meeting",
        start_time=datetime(2026, 9, 17, 14, 0),
        duration_minutes=60,
    )

    assert meeting.end_time == datetime(
        2026, 9, 17, 15, 0
    )


def test_meeting_without_url():
    meeting = Meeting(
        title="Team Sync",
        start_time=datetime(2026, 9, 17, 10, 0),
        duration_minutes=30,
        participants=[
            "Manager",
            "Developer",
        ],
    )

    meeting.validate()

    assert meeting.meeting_url is None


def test_multiple_participants():
    meeting = Meeting(
        title="Project Meeting",
        start_time=datetime(2026, 9, 17, 11, 0),
        duration_minutes=45,
        participants=[
            "Manager",
            "Tech Lead",
            "Developer",
        ],
    )

    meeting.validate()

    assert len(meeting.participants) == 3


def test_empty_title_is_invalid():
    meeting = Meeting(
        title="",
        start_time=datetime(2026, 9, 17, 14, 0),
        duration_minutes=60,
    )

    with pytest.raises(ValueError):
        meeting.validate()


def test_invalid_duration_is_rejected():
    meeting = Meeting(
        title="Invalid Meeting",
        start_time=datetime(2026, 9, 17, 14, 0),
        duration_minutes=0,
    )

    with pytest.raises(ValueError):
        meeting.validate()


def test_invalid_participants_are_rejected():
    meeting = Meeting(
        title="Invalid Meeting",
        start_time=datetime(2026, 9, 17, 14, 0),
        duration_minutes=30,
        participants=["Manager", ""],
    )

    with pytest.raises(ValueError):
        meeting.validate()