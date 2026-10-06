import logging
import threading
from shared.logging_config import setup_logging

from agent1_work_tracker.agent import (
    run_agent as run_work_tracker,
)
from agent2_meeting_agent.agent import (
    run_agent as run_meeting_agent,
)


def main():
    setup_logging()

    logger = logging.getLogger(__name__)

    stop_event = threading.Event()

    work_tracker_thread = threading.Thread(
        target=run_work_tracker,
        args=(stop_event,),
        name="WorkTrackerAgent",
    )

    meeting_agent_thread = threading.Thread(
        target=run_meeting_agent,
        args=(stop_event,),
        name="MeetingAgent",
    )

    logger.info("Starting Desktop AI Automation")

    work_tracker_thread.start()
    meeting_agent_thread.start()

    try:
        while True:
            work_tracker_thread.join(timeout=1)
            meeting_agent_thread.join(timeout=1)

            if (
                not work_tracker_thread.is_alive()
                and not meeting_agent_thread.is_alive()
            ):
                break

    except KeyboardInterrupt:
        logger.info("Shutdown requested")

    finally:
        stop_event.set()

        logger.info("Waiting for agents to stop")

        work_tracker_thread.join()
        meeting_agent_thread.join()

        logger.info("Desktop AI Automation stopped")


if __name__ == "__main__":
    main()