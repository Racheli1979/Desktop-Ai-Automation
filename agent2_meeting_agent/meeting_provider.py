from datetime import datetime, timedelta

from .meeting import Meeting
from .meeting_source import get_meetings


UPCOMING_WINDOW_MINUTES = 10


class MeetingProvider:
    def __init__(
        self,
        meeting_source=get_meetings,
        upcoming_window_minutes: int = UPCOMING_WINDOW_MINUTES,
    ):
        self.meeting_source = meeting_source
        self.upcoming_window_minutes = upcoming_window_minutes
        self.processed_meetings: set[str] = set()

    def get_upcoming_meetings(
        self,
        current_time: datetime,
    ) -> list[Meeting]:
        
        meetings = self.meeting_source()
        upcoming = []

        window_end = (
            current_time
            + timedelta(
                minutes=self.upcoming_window_minutes
            )
        )

        for meeting in meetings:

            meeting_id = self._get_meeting_id(meeting)

            if meeting_id in self.processed_meetings:
                continue

            if meeting.start_time <= current_time:
                continue

            if meeting.start_time > window_end:
                continue

            upcoming.append(meeting)

        return upcoming

    def mark_as_processed(
        self,
        meeting: Meeting,
    ) -> None:
        self.processed_meetings.add(
            self._get_meeting_id(meeting)
        )

    @staticmethod
    def _get_meeting_id(
        meeting: Meeting,
    ) -> str:
        return (
            f"{meeting.title}|"
            f"{meeting.start_time.isoformat()}"
        )