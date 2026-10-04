from dataclasses import dataclass
import logging
import time
import webbrowser

import psutil
import win32con
import win32gui
import win32process


logger = logging.getLogger(__name__)


@dataclass
class DesktopWindow:
    handle: int
    title: str
    process_id: int
    process_name: str

PROTECTED_PROCESS_NAMES = {
    "dwm.exe",
    "winlogon.exe",
    "csrss.exe",
    "lsass.exe",
    "services.exe",
    "smss.exe",
    "system",
    "system idle process",
}

PROTECTED_WINDOW_CLASSES = {
    "Progman",
    "WorkerW",
    "Shell_TrayWnd",
    "Shell_SecondaryTrayWnd",
}


def get_open_windows() -> list[DesktopWindow]:

    windows: list[DesktopWindow] = []

    def enum_window_callback(hwnd: int, _: int) -> None:
        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd).strip()

        if not title:
            return

        class_name = win32gui.GetClassName(hwnd)

        if class_name in PROTECTED_WINDOW_CLASSES:
            return

        _, process_id = win32process.GetWindowThreadProcessId(hwnd)

        try:
            process_name = psutil.Process(process_id).name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            logger.warning(
                "Could not read process information for window: %s",
                title,
            )
            return

        if process_name.lower() in PROTECTED_PROCESS_NAMES:
            return

        windows.append(
            DesktopWindow(
                handle=hwnd,
                title=title,
                process_id=process_id,
                process_name=process_name,
            )
        )

    win32gui.EnumWindows(enum_window_callback, 0)

    return windows


def close_window(
    window: DesktopWindow,
    timeout_seconds: float = 2.0,
) -> bool:

    if window.process_name.lower() in PROTECTED_PROCESS_NAMES:
        logger.warning(
            "Protected process cannot be closed: %s",
            window.process_name,
        )
        return False

    if not win32gui.IsWindow(window.handle):
        logger.warning(
            "Window no longer exists: %s",
            window.title,
        )
        return False

    try:
        win32gui.PostMessage(
            window.handle,
            win32con.WM_CLOSE,
            0,
            0,
        )

        start_time = time.monotonic()

        while time.monotonic() - start_time < timeout_seconds:
            if not win32gui.IsWindow(window.handle):
                logger.info(
                    "Window closed successfully: %s",
                    window.title,
                )
                return True

            time.sleep(0.1)

        logger.warning(
            "Window is still open after close request: %s",
            window.title,
        )

        return False

    except Exception:
        logger.exception(
            "Failed to close window: %s",
            window.title,
        )
        return False


def close_open_windows() -> list[tuple[DesktopWindow, bool]]:

    windows = get_open_windows()

    results: list[tuple[DesktopWindow, bool]] = []

    for window in windows:
        success = close_window(window)
        results.append((window, success))

    return results


def open_meeting_url(meeting_url: str) -> bool:

    if not meeting_url:
        logger.error("Meeting URL is empty")
        return False

    if not meeting_url.startswith(("http://", "https://")):
        logger.error("Invalid meeting URL")
        return False

    try:
        opened = webbrowser.open(meeting_url, new=2)

        if not opened:
            logger.error("Could not open meeting URL")
            return False

        logger.info("Meeting URL opened successfully")

        return True

    except Exception:
        logger.exception("Failed to open meeting URL")
        return False