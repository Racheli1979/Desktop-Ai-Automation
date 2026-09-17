from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class Meeting:
    title: str
    start_time: datetime
    duration_minutes: int
    participants: list[str] = field(default_factory=list)
    description: str = ""
    meeting_url: str | None = None

    def validate(self) -> None:
        if not self.title.strip():
            raise ValueError("Meeting title cannot be empty")

        if not isinstance(self.start_time, datetime):
            raise ValueError(
                "Start time must be a datetime object"
            )

        if self.duration_minutes <= 0:
            raise ValueError(
                "Meeting duration must be greater than 0"
            )

        if any(
            not participant.strip()
            for participant in self.participants
        ):
            raise ValueError(
                "Participants must contain valid names"
            )

    @property
    def end_time(self) -> datetime:
        return self.start_time + timedelta(
            minutes=self.duration_minutes
        )
