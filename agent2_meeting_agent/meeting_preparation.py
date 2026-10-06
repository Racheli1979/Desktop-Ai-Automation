import logging

from .meeting import Meeting
from .meeting_classifier import MeetingDecision
from .desktop_controller import (
    minimize_open_windows,
    open_meeting_url,
)


logger = logging.getLogger(__name__)


def prepare_desktop_for_meeting(
    meeting: Meeting,
    decision: MeetingDecision,
) -> bool:

    logger.debug(
        "Preparing desktop for meeting: %s",
        meeting.title,
    )

    if not decision.important:
        logger.debug(
            "Meeting is not important. No desktop preparation required: %s",
            meeting.title,
        )
        return False

    logger.debug(
        "Meeting classified as important: %s. "
        "Starting desktop preparation.",
        meeting.title,
    )

    minimize_results = minimize_open_windows()

    failed_closures = [
        window
        for window, success in minimize_results
        if not success
    ]

    if failed_closures:
        logger.warning(
            "Some application windows could not be minimized: %s",
            [window.title for window in failed_closures],
        )

    if not meeting.meeting_url:
        logger.error(
            "Important meeting has no meeting URL: %s",
            meeting.title,
        )
        return False

    meeting_opened = open_meeting_url(meeting.meeting_url)

    if not meeting_opened:
        logger.error(
            "Failed to open meeting URL: %s",
            meeting.meeting_url,
        )
        return False

    logger.info(
        "Desktop preparation completed successfully for meeting: %s",
        meeting.title,
    )

    return True