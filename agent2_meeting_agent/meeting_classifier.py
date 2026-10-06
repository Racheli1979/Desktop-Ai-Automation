# import json
# import logging
# from dataclasses import dataclass

# from .llm_client import create_llm
# from .meeting import Meeting


# logger = logging.getLogger(__name__)


# @dataclass
# class MeetingDecision:
#     important: bool
#     reason: str


# SYSTEM_PROMPT = """
# You are a Meeting Importance Classifier.

# Your task is to determine whether an upcoming meeting is important
# enough to trigger desktop preparation.

# Consider a meeting important when it involves:
# - important project decisions
# - blockers or critical issues
# - management or leadership
# - important reviews or presentations
# - meetings requiring immediate attention

# Consider a meeting not important when it is:
# - a routine status update
# - a casual or informational meeting
# - a meeting that does not require immediate attention

# Return ONLY valid JSON in this exact format:

# {
#     "important": true,
#     "reason": "Short explanation"
# }

# The "important" field must be a boolean: true or false.
# The "reason" field must be a short string.
# """


# class MeetingClassifier:
#     def __init__(self):
#         self.llm = create_llm()

#     def classify(self, meeting: Meeting) -> MeetingDecision:
#         prompt = self._build_prompt(meeting)

#         logger.info(
#             "Classifying meeting: %s at %s",
#             meeting.title,
#             meeting.start_time.strftime("%H:%M"),
#         )

#         response = self.llm.invoke(
#             [
#                 ("system", SYSTEM_PROMPT),
#                 ("human", prompt),
#             ]
#         )

#         decision = self._parse_response(response.content)

#         logger.info(
#             "Meeting decision: title=%s important=%s reason=%s",
#             meeting.title,
#             decision.important,
#             decision.reason,
#         )

#         return decision

#     @staticmethod
#     def _build_prompt(meeting: Meeting) -> str:
#         participants = ", ".join(meeting.participants) or "None"

#         return f"""
# Meeting information:

# Title: {meeting.title}
# Start time: {meeting.start_time.strftime("%Y-%m-%d %H:%M")}
# Duration: {meeting.duration_minutes} minutes
# Participants: {participants}
# Description: {meeting.description or "None"}

# Determine whether this meeting is important enough
# to trigger desktop preparation.
# """

#     @staticmethod
#     def _parse_response(content: str) -> MeetingDecision:
#         try:
#             data = json.loads(content)

#             if not isinstance(data, dict):
#                 raise ValueError("AI response must be a JSON object")

#             important = data.get("important")
#             reason = data.get("reason")

#             if not isinstance(important, bool):
#                 raise ValueError(
#                     "AI decision 'important' must be a boolean"
#                 )

#             if not isinstance(reason, str) or not reason.strip():
#                 raise ValueError(
#                     "AI decision 'reason' must be a non-empty string"
#                 )

#             return MeetingDecision(
#                 important=important,
#                 reason=reason.strip(),
#             )

#         except (json.JSONDecodeError, ValueError, TypeError) as error:
#             logger.error(
#                 "Invalid AI meeting decision: %s",
#                 error,
#             )
#             raise ValueError(
#                 "Invalid AI response. No desktop action should be performed."
#             ) from error




import json
import logging
import os
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
        self.mode = os.getenv("AI_MODE", "demo").lower()
        self.llm = None

        if self.mode == "ai":
            self.llm = create_llm()
            logger.info("Meeting Classifier initialized in AI mode")

        else:
            logger.info("Meeting Classifier initialized in DEMO mode")

    def classify(self, meeting: Meeting) -> MeetingDecision:

        logger.info(
            "Classifying meeting: %s at %s",
            meeting.title,
            meeting.start_time.strftime("%H:%M"),
        )

        # ==========================================
        # DEMO / OFFLINE MODE
        # ==========================================
        if self.mode == "demo":
            return self._classify_demo(meeting)

        # ==========================================
        # REAL AI MODE
        # ==========================================
        if self.mode == "ai":
            return self._classify_with_ai(meeting)

        raise ValueError(
            f"Unsupported AI_MODE: {self.mode}. "
            "Use 'demo' or 'ai'."
        )

    def _classify_demo(self, meeting: Meeting) -> MeetingDecision:
        """
        Offline demo classification.

        No OpenAI API.
        No internet connection.
        No LLM.
        """

        title = meeting.title.lower()
        description = (meeting.description or "").lower()

        text = f"{title} {description}"

        important_keywords = [
            "urgent",
            "important",
            "critical",
            "project review",
            "presentation",
            "management",
            "leadership",
            "blocker",
            "interview",
        ]

        for keyword in important_keywords:
            if keyword in text:
                decision = MeetingDecision(
                    important=True,
                    reason=f"Demo classification: keyword '{keyword}' "
                           "indicates an important meeting.",
                )

                logger.info(
                    "DEMO decision: important=%s reason=%s",
                    decision.important,
                    decision.reason,
                )

                return decision

        decision = MeetingDecision(
            important=False,
            reason="Demo classification: no important keywords detected.",
        )

        logger.info(
            "DEMO decision: important=%s reason=%s",
            decision.important,
            decision.reason,
        )

        return decision

    def _classify_with_ai(
        self,
        meeting: Meeting,
    ) -> MeetingDecision:

        if self.llm is None:
            raise RuntimeError(
                "AI mode is enabled but the LLM was not initialized."
            )

        prompt = self._build_prompt(meeting)

        response = self.llm.invoke(
            [
                ("system", SYSTEM_PROMPT),
                ("human", prompt),
            ]
        )

        decision = self._parse_response(response.content)

        logger.info(
            "AI decision: title=%s important=%s reason=%s",
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
