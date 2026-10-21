from datetime import datetime, timedelta
from threading import Event
from unittest.mock import MagicMock, patch

from agent2_meeting_agent.meeting import Meeting
from agent2_meeting_agent.meeting_classifier import MeetingDecision
from agent2_meeting_agent.agent import run_agent


def create_meeting():
    return Meeting(
        title="Critical Project Review",
        start_time=datetime.now() - timedelta(minutes=1),
        duration_minutes=30,
        participants=["Project Manager"],
        description="Review critical project blockers",
        meeting_url="https://meet.google.com/example",
    )


@patch("agent2_meeting_agent.agent.MeetingClassifier")
@patch("agent2_meeting_agent.agent.MeetingProvider")
@patch("agent2_meeting_agent.agent.prepare_desktop_for_meeting")
def test_important_meeting_prepares_desktop(
    mock_prepare,
    mock_provider_class,
    mock_classifier_class,
):
    meeting = create_meeting()

    provider = mock_provider_class.return_value
    provider.get_upcoming_meetings.return_value = [meeting]

    classifier = mock_classifier_class.return_value
    classifier.classify.return_value = MeetingDecision(
        important=True,
        reason="Critical project blockers",
    )

    stop_event = MagicMock(spec=Event)
    stop_event.is_set.side_effect = [False, True]

    run_agent(stop_event)

    mock_prepare.assert_called_once_with(
        meeting,
        classifier.classify.return_value,
    )
    provider.mark_as_processed.assert_called_once_with(meeting)


@patch("agent2_meeting_agent.agent.MeetingClassifier")
@patch("agent2_meeting_agent.agent.MeetingProvider")
@patch("agent2_meeting_agent.agent.prepare_desktop_for_meeting")
def test_unimportant_meeting_does_not_prepare_desktop(
    mock_prepare,
    mock_provider_class,
    mock_classifier_class,
):
    meeting = create_meeting()

    provider = mock_provider_class.return_value
    provider.get_upcoming_meetings.return_value = [meeting]

    classifier = mock_classifier_class.return_value
    classifier.classify.return_value = MeetingDecision(
        important=False,
        reason="Routine update",
    )

    stop_event = MagicMock(spec=Event)
    stop_event.is_set.side_effect = [False, True]

    run_agent(stop_event)

    mock_prepare.assert_not_called()
    provider.mark_as_processed.assert_called_once_with(meeting)
