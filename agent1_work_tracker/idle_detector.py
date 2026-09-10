import ctypes


def get_idle_seconds():

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_uint),
            ("dwTime", ctypes.c_uint),
        ]

    last_input = LASTINPUTINFO()
    last_input.cbSize = ctypes.sizeof(LASTINPUTINFO)

    ctypes.windll.user32.GetLastInputInfo(
        ctypes.byref(last_input)
    )

    current_tick = ctypes.windll.kernel32.GetTickCount()

    idle_time = current_tick - last_input.dwTime

    return idle_time / 1000.0


def is_idle(timeout_seconds=60):
    return get_idle_seconds() >= timeout_seconds