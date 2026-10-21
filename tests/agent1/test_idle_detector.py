from datetime import datetime
from types import SimpleNamespace

from agent1_work_tracker import idle_detector


def test_get_idle_seconds(monkeypatch):
    def fake_get_last_input_info(pointer):
        pointer._obj.dwTime = 1000
        return 1

    fake_user32 = SimpleNamespace(
        GetLastInputInfo=fake_get_last_input_info
    )

    fake_kernel32 = SimpleNamespace(
        GetTickCount=lambda: 3500
    )

    fake_windll = SimpleNamespace(
        user32=fake_user32,
        kernel32=fake_kernel32,
    )

    monkeypatch.setattr(
        idle_detector.ctypes,
        "windll",
        fake_windll,
    )

    result = idle_detector.get_idle_seconds()

    assert result == 2.5


def test_get_idle_seconds_when_api_fails(
    monkeypatch,
):
    fake_user32 = SimpleNamespace(
        GetLastInputInfo=lambda pointer: 0
    )

    fake_kernel32 = SimpleNamespace(
        GetTickCount=lambda: 3500
    )

    fake_windll = SimpleNamespace(
        user32=fake_user32,
        kernel32=fake_kernel32,
    )

    monkeypatch.setattr(
        idle_detector.ctypes,
        "windll",
        fake_windll,
    )

    result = idle_detector.get_idle_seconds()

    assert result == 0.0


def test_get_last_input_time(monkeypatch):
    monkeypatch.setattr(
        idle_detector,
        "get_idle_seconds",
        lambda: 5.0,
    )

    before = datetime.now()

    result = idle_detector.get_last_input_time()

    after = datetime.now()

    assert isinstance(result, datetime)

    assert result <= after
    assert result >= (
        before
        - idle_detector.timedelta(seconds=5.1)
    )