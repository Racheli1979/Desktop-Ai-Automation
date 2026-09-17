from datetime import datetime

from .meeting import Meeting


def get_meetings() -> list[Meeting]:
    return [
        Meeting(
            title="Project Review",
            start_time=datetime(2026, 9, 17, 14, 0),
            duration_minutes=60,
            participants=[
                "Manager",
                "Tech Lead",
            ],
            description="Discuss project decisions",
            meeting_url="https://meet.google.com/example",
        ),
        Meeting(
            title="Team Sync",
            start_time=datetime(2026, 9, 17, 15, 30),
            duration_minutes=30,
            participants=[
                "Developer",
            ],
            description="Weekly team sync",
        ),
    ]