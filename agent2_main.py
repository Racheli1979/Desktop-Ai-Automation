import logging
import threading

import keyring

from shared.logging_config import setup_logging
from setup_user_config import main as setup_user_config

from agent2_meeting_agent.agent import run_agent as run_meeting_agent


SERVICE_NAME = "DesktopAiAutomation"
OPENAI_KEY_NAME = "openai_api_key"


def ensure_openai_api_key() -> bool:
    api_key = keyring.get_password(
        SERVICE_NAME,
        OPENAI_KEY_NAME,
    )

    if api_key:
        return True

    setup_user_config()

    return bool(
        keyring.get_password(
            SERVICE_NAME,
            OPENAI_KEY_NAME,
        )
    )


def main():
    setup_logging()

    logger = logging.getLogger(__name__)

    if not ensure_openai_api_key():
        logger.error(
            "OpenAI API key is not configured. "
            "The Meeting Agent will not start."
        )
        return

    stop_event = threading.Event()

    logger.info("Starting Meeting Agent")

    try:
        run_meeting_agent(stop_event)

    except KeyboardInterrupt:
        logger.info("Shutdown requested")

    finally:
        stop_event.set()
        logger.info("Meeting Agent stopped")


if __name__ == "__main__":
    main()