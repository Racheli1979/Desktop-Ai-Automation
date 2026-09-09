import ctypes
import win32gui
import win32process
import psutil
from datetime import datetime


def get_product_name(exe_path):
    try:
        size = ctypes.windll.version.GetFileVersionInfoSizeW(exe_path, None)

        if not size:
            return None

        buffer = ctypes.create_string_buffer(size)

        ctypes.windll.version.GetFileVersionInfoW(
            exe_path,
            0,
            size,
            buffer
        )

        translation = ctypes.c_void_p()
        translation_size = ctypes.c_uint()

        ctypes.windll.version.VerQueryValueW(
            buffer,
            "\\VarFileInfo\\Translation",
            ctypes.byref(translation),
            ctypes.byref(translation_size)
        )

        if not translation_size.value:
            return None

        lang = ctypes.cast(
            translation,
            ctypes.POINTER(ctypes.c_ushort)
        )

        language = lang[0]
        codepage = lang[1]

        sub_block = (
            f"\\StringFileInfo\\{language:04x}{codepage:04x}\\ProductName"
        )

        value = ctypes.c_void_p()
        value_size = ctypes.c_uint()

        result = ctypes.windll.version.VerQueryValueW(
            buffer,
            sub_block,
            ctypes.byref(value),
            ctypes.byref(value_size)
        )

        if result and value.value:
            return ctypes.wstring_at(value.value)

    except Exception:
        pass

    return None


def get_active_app():
    hwnd = win32gui.GetForegroundWindow()

    _, pid = win32process.GetWindowThreadProcessId(hwnd)

    process = psutil.Process(pid)

    try:
        exe_path = process.exe()

        product_name = get_product_name(exe_path)

        if product_name:
            return product_name

        return process.name()

    except Exception:
        return process.name()


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"{timestamp}    {get_active_app()}")