import logging
from datetime import datetime

from .usage_tracker import ActivityTracker


logger = logging.getLogger(__name__)


def run_agent(stop_event):
    logger.info("Work Tracker Agent started")

    tracker = ActivityTracker()

    try:
        while not stop_event.is_set():
            tracker.update()
            stop_event.wait(tracker.check_interval)

    except Exception:
        logger.exception("Work Tracker Agent failed")
        raise

    finally:
        tracker.stop_tracking(datetime.now())
        logger.info("Work Tracker Agent stopped")