from datetime import datetime

import pytest

from agent2_meeting_agent.meeting import Meeting
from agent2_meeting_agent.meeting_classifier import MeetingClassifier


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    def __init__(self, response):
        self.response = response

    def invoke(self, messages):
        return FakeResponse(self.response)


def create_meeting():
    return Meeting(
        title="Project Review",
        start_time=datetime(2026, 9, 17, 14, 0),
        duration_minutes=60,
        participants=["Manager", "Tech Lead"],
        description="Discuss project decisions",
    )


def test_classify_important_meeting():
    classifier = MeetingClassifier.__new__(MeetingClassifier)

    classifier.llm = FakeLLM(
        '{"important": true, '
        '"reason": "Important project decisions."}'
    )

    decision = classifier.classify(create_meeting())

    assert decision.important is True
    assert decision.reason == "Important project decisions."


def test_classify_not_important_meeting():
    classifier = MeetingClassifier.__new__(MeetingClassifier)

    classifier.llm = FakeLLM(
        '{"important": false, '
        '"reason": "Routine status update."}'
    )

    decision = classifier.classify(create_meeting())

    assert decision.important is False


def test_invalid_ai_response_is_rejected():
    classifier = MeetingClassifier.__new__(MeetingClassifier)

    classifier.llm = FakeLLM(
        "This meeting seems important."
    )

    with pytest.raises(ValueError):
        classifier.classify(create_meeting())


def test_invalid_important_value_is_rejected():
    classifier = MeetingClassifier.__new__(MeetingClassifier)

    classifier.llm = FakeLLM(
        '{"important": "yes", '
        '"reason": "Important meeting."}'
    )

    with pytest.raises(ValueError):
        classifier.classify(create_meeting())