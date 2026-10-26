import logging
import os
import subprocess
import sys
from pathlib import Path

import psutil
import win32com.client
import win32event
import win32api
import winerror

from shared.logging_config import setup_logging


APP_NAME = "Desktop AI Automation"

AGENT1_NAME = "WorkTrackerAgent.exe"
AGENT2_NAME = "MeetingAgent.exe"

MUTEX_NAME = "DesktopAiAutomation_WorkTracker"


def get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    return Path(__file__).resolve().parent


APP_DIR = get_app_dir()

AGENT1_EXE = APP_DIR / "WorkTrackerAgent" / AGENT1_NAME
AGENT2_EXE = APP_DIR / "MeetingAgent" / AGENT2_NAME

STARTUP_DIR = (
    Path(os.environ["APPDATA"])
    / "Microsoft"
    / "Windows"
    / "Start Menu"
    / "Programs"
    / "Startup"
)

STARTUP_SHORTCUT = STARTUP_DIR / "Work Tracker.lnk"


def is_agent1_running() -> bool:
    for process in psutil.process_iter(["name"]):
        try:
            process_name = process.info["name"] or ""

            if process_name.casefold() == AGENT1_NAME.casefold():
                return True

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return False


def acquire_agent1_mutex():
    mutex = win32event.CreateMutex(
        None,
        False,
        MUTEX_NAME,
    )

    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        return None

    return mutex


def start_agent1() -> None:
    if is_agent1_running():
        logging.info("Work Tracker is already running")
        return

    logging.info("Starting Work Tracker")

    subprocess.Popen(
        [str(AGENT1_EXE)],
        cwd=str(AGENT1_EXE.parent),
        close_fds=True,
    )


def configure_agent1_startup() -> None:
    STARTUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    shell = win32com.client.Dispatch("WScript.Shell")

    shortcut = shell.CreateShortCut(
        str(STARTUP_SHORTCUT)
    )

    shortcut.TargetPath = str(AGENT1_EXE)
    shortcut.WorkingDirectory = str(AGENT1_EXE.parent)
    shortcut.Description = (
        "Start Work Tracker when Windows starts"
    )
    shortcut.WindowStyle = 7

    shortcut.Save()

    logging.info(
        "Work Tracker startup configured: %s",
        STARTUP_SHORTCUT,
    )


def start_agent2() -> None:
    logging.info("Starting Meeting Agent")

    subprocess.Popen(
        [str(AGENT2_EXE)],
        cwd=str(AGENT2_EXE.parent),
        close_fds=True,
    )


def main() -> None:
    setup_logging()

    logger = logging.getLogger(__name__)

    if not AGENT1_EXE.is_file():
        logger.error(
            "Work Tracker executable not found: %s",
            AGENT1_EXE,
        )
        return

    if not AGENT2_EXE.is_file():
        logger.error(
            "Meeting Agent executable not found: %s",
            AGENT2_EXE,
        )
        return

    mutex = acquire_agent1_mutex()

    try:
        if mutex is not None:
            start_agent1()

            if not STARTUP_SHORTCUT.exists():
                configure_agent1_startup()
        else:
            logger.info(
                "Another Launcher instance is already "
                "managing Work Tracker"
            )

        start_agent2()

        logger.info(
            "%s launched successfully",
            APP_NAME,
        )

    except Exception:
        logger.exception(
            "Failed to launch application"
        )

    finally:
        if mutex is not None:
            win32api.CloseHandle(mutex)


if __name__ == "__main__":
    main()