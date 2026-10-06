from datetime import datetime, timedelta

from .meeting import Meeting

MEETING_START = datetime.now() + timedelta(minutes=0.3)


def get_meetings() -> list[Meeting]:
    return [
        Meeting(
            title="Urgent Project Meeting",
            start_time=MEETING_START,
            duration_minutes=30,
            participants=[
                "Manager",
                "Tech Lead",
            ],
            description="Urgent project decision",
            meeting_url="https://meet.google.com/example",
        ),
        Meeting(
            title="Team Coffee Chat",
            start_time=MEETING_START + timedelta(minutes=2),
            duration_minutes=30,
            participants=[
                "Developer",
            ],
            description="Casual team conversation",
        )
    ]