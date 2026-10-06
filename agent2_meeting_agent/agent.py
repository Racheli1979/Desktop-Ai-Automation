import logging
from datetime import datetime

from .meeting_classifier import MeetingClassifier
from .meeting_preparation import prepare_desktop_for_meeting
from .meeting_provider import MeetingProvider

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 30


def run_agent(stop_event):
    logger.info("Meeting Agent started")

    provider = MeetingProvider()
    classifier = MeetingClassifier()

    pending_meetings = {}

    try:
        while not stop_event.is_set():
            current_time = datetime.now()

            for meeting_key, (
                meeting,
                decision,
            ) in list(pending_meetings.items()):

                if current_time >= meeting.start_time:
                    logger.info(
                        "Meeting has started: %s | start_time=%s | now=%s",
                        meeting.title,
                        meeting.start_time,
                        current_time,
                    )

                    prepare_desktop_for_meeting(
                        meeting,
                        decision,
                    )

                    provider.mark_as_processed(meeting)

                    del pending_meetings[meeting_key]

            meetings = provider.get_upcoming_meetings(
                current_time
            )

            for meeting in meetings:
                meeting_key = meeting.title

                if meeting_key in pending_meetings:
                    continue

                logger.debug(
                    "Processing upcoming meeting: %s | start_time=%s",
                    meeting.title,
                    meeting.start_time,
                )

                try:
                    decision = classifier.classify(meeting)

                except Exception:
                    logger.exception(
                        "Failed to classify meeting: %s",
                        meeting.title,
                    )
                    continue

                if not decision.important:
                    logger.info(
                        "Meeting is not important: %s",
                        meeting.title,
                    )

                    provider.mark_as_processed(meeting)
                    continue

                if current_time < meeting.start_time:
                    pending_meetings[meeting_key] = (
                        meeting,
                        decision,
                    )

                    logger.info(
                        "Important meeting detected. "
                        "Waiting until start time: %s",
                        meeting.start_time,
                    )

                    continue

                prepare_desktop_for_meeting(
                    meeting,
                    decision,
                )

                provider.mark_as_processed(meeting)

            stop_event.wait(CHECK_INTERVAL_SECONDS)

    except Exception:
        logger.exception("Meeting Agent failed")
        raise

    finally:
        logger.info("Meeting Agent stopped")