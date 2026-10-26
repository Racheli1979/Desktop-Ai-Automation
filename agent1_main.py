import logging
import threading

from shared.logging_config import setup_logging
from agent1_work_tracker.agent import run_agent as run_work_tracker
from agent1_work_tracker.system_tray import WorkTrackerTray


def main():
    setup_logging()

    logger = logging.getLogger(__name__)
    stop_event = threading.Event()

    tray = WorkTrackerTray(stop_event)

    worker = threading.Thread(
        target=run_work_tracker,
        args=(stop_event,),
        name="WorkTracker",
        daemon=False,
    )

    logger.info("Starting Work Tracker Agent in background")

    worker.start()

    try:
        tray.run()
    except Exception:
        logger.exception("System Tray failed")
        stop_event.set()
    finally:
        stop_event.set()
        tray.stop()
        worker.join()
        logger.info("Work Tracker Agent stopped")


if __name__ == "__main__":
    main()