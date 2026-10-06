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
    """
    Return all visible application windows that are safe to process.
    """

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


# def close_window(
#     window: DesktopWindow,
# ) -> bool:
#     """
#     Request a single window to close.

#     WM_CLOSE gives the application an opportunity to save data
#     or ask the user what to do with unsaved changes.
#     """

#     if window.process_name.lower() in PROTECTED_PROCESS_NAMES:
#         logger.warning(
#             "Protected process cannot be closed: %s",
#             window.process_name,
#         )
#         return False

#     if not win32gui.IsWindow(window.handle):
#         logger.warning(
#             "Window no longer exists: %s",
#             window.title,
#         )
#         return False

#     try:
#         win32gui.PostMessage(
#             window.handle,
#             win32con.WM_CLOSE,
#             0,
#             0,
#         )

#         logger.info(
#             "Close request sent: %s | process=%s",
#             window.title,
#             window.process_name,
#         )

#         return True

#     except Exception:
#         logger.exception(
#             "Failed to send close request: %s",
#             window.title,
#         )
#         return False

def minimize_window(window: DesktopWindow) -> bool:
    """Minimize a single application window."""

    if not win32gui.IsWindow(window.handle):
        logger.warning(
            "Window no longer exists: %s",
            window.title,
        )
        return False

    try:
        win32gui.ShowWindow(
            window.handle,
            win32con.SW_MINIMIZE,
        )

        logger.info(
            "Window minimized: %s | process=%s",
            window.title,
            window.process_name,
        )

        return True

    except Exception:
        logger.exception(
            "Failed to minimize window: %s",
            window.title,
        )
        return False

# def close_open_windows(
#     timeout_seconds: float = 3.0,
# ) -> list[tuple[DesktopWindow, bool]]:
#     """
#     Request all eligible windows to close and verify the result.

#     All close requests are sent first so one slow application
#     does not prevent the other applications from receiving
#     their close requests.
#     """

#     windows = get_open_windows()

#     logger.info(
#         "Found %d open windows",
#         len(windows),
#     )

#     for window in windows:
#         logger.info(
#             "FOUND WINDOW: %s | process=%s | pid=%s",
#             window.title,
#             window.process_name,
#             window.process_id,
#         )

#     if not windows:
#         logger.info("No application windows found to close")
#         return []

#     results: list[tuple[DesktopWindow, bool]] = []

#     # First send close requests to ALL windows.
#     for window in windows:
#         close_window(window)

#     # Give applications time to process WM_CLOSE.
#     deadline = time.monotonic() + timeout_seconds

#     remaining_windows = windows.copy()

#     while remaining_windows and time.monotonic() < deadline:
#         still_open = []

#         for window in remaining_windows:
#             if win32gui.IsWindow(window.handle):
#                 still_open.append(window)
#             else:
#                 logger.info(
#                     "Window closed successfully: %s",
#                     window.title,
#                 )

#         remaining_windows = still_open

#         if remaining_windows:
#             time.sleep(0.1)

#     # Build final result for every window.
#     for window in windows:
#         is_closed = not win32gui.IsWindow(window.handle)

#         if is_closed:
#             logger.info(
#                 "Window closed: %s",
#                 window.title,
#             )
#         else:
#             logger.warning(
#                 "Window is still open after close request: %s",
#                 window.title,
#             )

#         results.append(
#             (window, is_closed)
#         )

#     closed_count = sum(
#         success
#         for _, success in results
#     )

#     failed_count = len(results) - closed_count

#     logger.info(
#         "Desktop close operation completed: "
#         "%d closed, %d still open",
#         closed_count,
#         failed_count,
#     )

#     return results

def minimize_open_windows() -> list[tuple[DesktopWindow, bool]]:
    """Minimize all eligible application windows."""

    windows = get_open_windows()

    logger.info(
        "Found %d open windows",
        len(windows),
    )

    results: list[tuple[DesktopWindow, bool]] = []

    for window in windows:
        success = minimize_window(window)
        results.append((window, success))

    logger.info(
        "Desktop minimize operation completed",
    )

    return results

def open_meeting_url(meeting_url: str) -> bool:
    """
    Open the meeting URL in the default browser.
    """

    if not meeting_url:
        logger.error("Meeting URL is empty")
        return False

    if not meeting_url.startswith(
        ("http://", "https://")
    ):
        logger.error(
            "Invalid meeting URL"
        )
        return False

    try:
        opened = webbrowser.open(
            meeting_url,
            new=2,
        )

        if not opened:
            logger.error(
                "Could not open meeting URL"
            )
            return False

        logger.info(
            "Meeting URL opened successfully: %s",
            meeting_url,
        )

        return True

    except Exception:
        logger.exception(
            "Failed to open meeting URL"
        )
        return False