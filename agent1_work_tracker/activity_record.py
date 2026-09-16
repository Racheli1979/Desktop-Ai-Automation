from dataclasses import dataclass
from datetime import datetime


VALID_STATUSES = {"Active", "Idle"}


@dataclass
class ActivityRecord:
    date: str
    application: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    status: str

    def validate(self) -> None:
        if not self.application:
            raise ValueError("Application cannot be empty")

        if self.end_time < self.start_time:
            raise ValueError(
                "End time cannot be before start time"
            )

        if self.duration_seconds < 0:
            raise ValueError(
                "Duration cannot be negative"
            )

        if self.status not in VALID_STATUSES:
            raise ValueError(
                "Status must be one of Active or Idle"
            )