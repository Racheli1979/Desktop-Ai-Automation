from agent1_work_tracker import active_app


class FakeProcess:
    def exe(self):
        return r"C:\Program Files\Microsoft VS Code\Code.exe"

    def name(self):
        return "Code.exe"


def test_get_product_name_invalid_path():
    result = active_app.get_product_name(
        r"C:\does_not_exist.exe"
    )

    assert result is None


def test_get_active_app_returns_product_name(monkeypatch):
    monkeypatch.setattr(
        active_app.win32gui,
        "GetForegroundWindow",
        lambda: 100,
    )

    monkeypatch.setattr(
        active_app.win32process,
        "GetWindowThreadProcessId",
        lambda hwnd: (1, 1234),
    )

    monkeypatch.setattr(
        active_app.psutil,
        "Process",
        lambda pid: FakeProcess(),
    )

    monkeypatch.setattr(
        active_app,
        "get_product_name",
        lambda path: "Visual Studio Code",
    )

    result = active_app.get_active_app()

    assert result == "Visual Studio Code"


def test_get_active_app_falls_back_to_process_name(
    monkeypatch,
):
    monkeypatch.setattr(
        active_app.win32gui,
        "GetForegroundWindow",
        lambda: 100,
    )

    monkeypatch.setattr(
        active_app.win32process,
        "GetWindowThreadProcessId",
        lambda hwnd: (1, 1234),
    )

    monkeypatch.setattr(
        active_app.psutil,
        "Process",
        lambda pid: FakeProcess(),
    )

    monkeypatch.setattr(
        active_app,
        "get_product_name",
        lambda path: None,
    )

    result = active_app.get_active_app()

    assert result == "Code.exe"