import ctypes
from datetime import datetime, timedelta


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_uint),
    ]


def get_idle_seconds():
    last_input = LASTINPUTINFO()
    last_input.cbSize = ctypes.sizeof(LASTINPUTINFO)

    ctypes.windll.user32.GetLastInputInfo(
        ctypes.byref(last_input)
    )

    current_tick = ctypes.windll.kernel32.GetTickCount()

    idle_time = current_tick - last_input.dwTime

    return idle_time / 1000.0


def get_last_input_time():
    """
    Returns the approximate time of the user's last
    keyboard or mouse input.
    """
    idle_seconds = get_idle_seconds()

    return datetime.now() - timedelta(seconds=idle_seconds)