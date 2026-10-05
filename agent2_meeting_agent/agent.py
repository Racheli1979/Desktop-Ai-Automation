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

    try:
        while not stop_event.is_set():
            current_time = datetime.now()

            meetings = provider.get_upcoming_meetings(
                current_time
            )

            for meeting in meetings:
                logger.info(
                    "Processing upcoming meeting: %s",
                    meeting.title,
                )

                try:
                    decision = classifier.classify(meeting)

                    logger.info(
                        "Meeting classification: %s | important=%s | reason=%s",
                        meeting.title,
                        decision.important,
                        decision.reason,
                    )

                except Exception:
                    logger.exception(
                        "Failed to classify meeting: %s",
                        meeting.title,
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