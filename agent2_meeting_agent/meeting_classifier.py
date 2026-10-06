import json
import logging
from dataclasses import dataclass

from .llm_client import create_llm
from .meeting import Meeting


logger = logging.getLogger(__name__)


@dataclass
class MeetingDecision:
    important: bool
    reason: str


SYSTEM_PROMPT = """
You are a Meeting Importance Classifier.

Your task is to determine whether an upcoming meeting is important
enough to trigger desktop preparation.

Consider a meeting important when it involves:
- important project decisions
- blockers or critical issues
- management or leadership
- important reviews or presentations
- meetings requiring immediate attention

Consider a meeting not important when it is:
- a routine status update
- a casual or informational meeting
- a meeting that does not require immediate attention

Return ONLY valid JSON in this exact format:

{
    "important": true,
    "reason": "Short explanation"
}

The "important" field must be a boolean: true or false.
The "reason" field must be a short string.
"""


class MeetingClassifier:
    def __init__(self):
        self.llm = create_llm()

    def classify(self, meeting: Meeting) -> MeetingDecision:
        prompt = self._build_prompt(meeting)

        logger.debug(
            "Classifying meeting: %s at %s",
            meeting.title,
            meeting.start_time.strftime("%H:%M"),
        )

        response = self.llm.invoke(
            [
                ("system", SYSTEM_PROMPT),
                ("human", prompt),
            ]
        )

        decision = self._parse_response(response.content)

        logger.info(
            "Meeting classified: title=%s | important=%s | reason=%s",
            meeting.title,
            decision.important,
            decision.reason,
        )

        return decision

    @staticmethod
    def _build_prompt(meeting: Meeting) -> str:
        participants = ", ".join(meeting.participants) or "None"

        return f"""
Meeting information:

Title: {meeting.title}
Start time: {meeting.start_time.strftime("%Y-%m-%d %H:%M")}
Duration: {meeting.duration_minutes} minutes
Participants: {participants}
Description: {meeting.description or "None"}

Determine whether this meeting is important enough
to trigger desktop preparation.
"""

    @staticmethod
    def _parse_response(content: str) -> MeetingDecision:
        try:
            data = json.loads(content)

            if not isinstance(data, dict):
                raise ValueError("AI response must be a JSON object")

            important = data.get("important")
            reason = data.get("reason")

            if not isinstance(important, bool):
                raise ValueError(
                    "AI decision 'important' must be a boolean"
                )

            if not isinstance(reason, str) or not reason.strip():
                raise ValueError(
                    "AI decision 'reason' must be a non-empty string"
                )

            return MeetingDecision(
                important=important,
                reason=reason.strip(),
            )

        except (json.JSONDecodeError, ValueError, TypeError) as error:
            logger.error(
                "Invalid AI meeting decision: %s",
                error,
            )
            raise ValueError(
                "Invalid AI response. No desktop action should be performed."
            ) from error