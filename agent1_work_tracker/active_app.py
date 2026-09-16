import ctypes
from datetime import datetime

import psutil
import win32gui
import win32process


def get_product_name(exe_path: str) -> str | None:
    try:
        size = ctypes.windll.version.GetFileVersionInfoSizeW(
            exe_path,
            None,
        )

        if not size:
            return None

        buffer = ctypes.create_string_buffer(size)

        ctypes.windll.version.GetFileVersionInfoW(
            exe_path,
            0,
            size,
            buffer,
        )

        translation = ctypes.c_void_p()
        translation_size = ctypes.c_uint()

        result = ctypes.windll.version.VerQueryValueW(
            buffer,
            "\\VarFileInfo\\Translation",
            ctypes.byref(translation),
            ctypes.byref(translation_size),
        )

        if not result or not translation_size.value:
            return None

        language_info = ctypes.cast(
            translation,
            ctypes.POINTER(ctypes.c_ushort),
        )

        language = language_info[0]
        codepage = language_info[1]

        sub_block = (
            f"\\StringFileInfo\\"
            f"{language:04x}{codepage:04x}\\ProductName"
        )

        value = ctypes.c_void_p()
        value_size = ctypes.c_uint()

        result = ctypes.windll.version.VerQueryValueW(
            buffer,
            sub_block,
            ctypes.byref(value),
            ctypes.byref(value_size),
        )

        if result and value.value:
            return ctypes.wstring_at(value.value)

    except OSError:
        return None

    return None


def get_active_app() -> str | None:
    hwnd = win32gui.GetForegroundWindow()

    if not hwnd:
        return None

    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)

        executable_path = process.exe()
        product_name = get_product_name(executable_path)

        return product_name or process.name()

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess,
        OSError,
    ):
        return None


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp}    {get_active_app()}")