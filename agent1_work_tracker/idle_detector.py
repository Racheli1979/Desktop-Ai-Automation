import ctypes
from datetime import datetime, timedelta


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_uint),
    ]


def get_idle_seconds() -> float:
    last_input = LASTINPUTINFO()
    last_input.cbSize = ctypes.sizeof(LASTINPUTINFO)

    result = ctypes.windll.user32.GetLastInputInfo(
        ctypes.byref(last_input)
    )

    if not result:
        return 0.0

    current_tick = ctypes.windll.kernel32.GetTickCount()

    idle_milliseconds = current_tick - last_input.dwTime

    return idle_milliseconds / 1000.0


def get_last_input_time() -> datetime:
    idle_seconds = get_idle_seconds()

    return datetime.now() - timedelta(
        seconds=idle_seconds
    )