import logging
from datetime import datetime

from .usage_tracker import ActivityTracker


logger = logging.getLogger(__name__)


def run_agent(stop_event):
    logger.info("Work Tracker Agent started")

    tracker = ActivityTracker()

    try:
        while not stop_event.is_set():
            try:
                tracker.update()
            except Exception:
                logger.exception("Work Tracker update failed")

            stop_event.wait(tracker.check_interval)

    finally:
        logger.info("Work Tracker shutdown started")

        try:
            tracker.stop_tracking(datetime.now())
        except Exception:
            logger.exception("Failed to stop Work Tracker cleanly")

        logger.info("Work Tracker stopped")