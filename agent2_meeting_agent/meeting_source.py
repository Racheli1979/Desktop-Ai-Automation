from datetime import datetime, timedelta

from .meeting import Meeting


def get_meetings() -> list[Meeting]:
    now = datetime.now()

    return [
        Meeting(
            title="Urgent Project Meeting",
            start_time=now + timedelta(minutes=2),
            duration_minutes=30,
            participants=[
                "Manager",
                "Tech Lead",
            ],
            description="Urgent project decision",
            meeting_url="https://meet.google.com/example",
        ),
        Meeting(
            title="Team Sync",
            start_time=now + timedelta(minutes=30),
            duration_minutes=30,
            participants=[
                "Developer",
            ],
            description="Weekly team sync",
        ),
    ]