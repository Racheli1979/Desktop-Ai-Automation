from unittest.mock import patch

from agent2_meeting_agent.desktop_controller import (
    DesktopWindow,
    close_open_windows,
    close_window,
    get_open_windows,
    open_meeting_url,
)


def test_get_open_windows_returns_visible_windows():
    fake_hwnd = 100

    def fake_enum_windows(callback, _):
        callback(fake_hwnd, 0)

    with (
        patch(
            "agent2_meeting_agent.desktop_controller.win32gui.EnumWindows",
            side_effect=fake_enum_windows,
        ),
        patch(
            "agent2_meeting_agent.desktop_controller.win32gui.IsWindowVisible",
            return_value=True,
        ),
        patch(
            "agent2_meeting_agent.desktop_controller.win32gui.GetWindowText",
            return_value="Visual Studio Code",
        ),
        patch(
            "agent2_meeting_agent.desktop_controller.win32gui.GetClassName",
            return_value="Chrome_WidgetWin_1",
        ),
        patch(
            "agent2_meeting_agent.desktop_controller.win32process.GetWindowThreadProcessId",
            return_value=(1, 1234),
        ),
        patch(
            "agent2_meeting_agent.desktop_controller.psutil.Process",
        ) as mock_process,
    ):
        mock_process.return_value.name.return_value = "Code.exe"

        windows = get_open_windows()

    assert len(windows) == 1
    assert windows[0].title == "Visual Studio Code"
    assert windows[0].process_id == 1234
    assert windows[0].process_name == "Code.exe"


def test_get_open_windows_ignores_hidden_windows():
    fake_hwnd = 100

    def fake_enum_windows(callback, _):
        callback(fake_hwnd, 0)

    with (
        patch(
            "agent2_meeting_agent.desktop_controller.win32gui.EnumWindows",
            side_effect=fake_enum_windows,
        ),
        patch(
            "agent2_meeting_agent.desktop_controller.win32gui.IsWindowVisible",
            return_value=False,
        ),
    ):
        windows = get_open_windows()

    assert windows == []


def test_close_window_returns_false_for_protected_process():
    window = DesktopWindow(
        handle=100,
        title="Windows System",
        process_id=1234,
        process_name="lsass.exe",
    )

    with patch(
        "agent2_meeting_agent.desktop_controller.win32gui.PostMessage"
    ) as mock_post_message:
        result = close_window(window)

    assert result is False
    mock_post_message.assert_not_called()


def test_close_window_returns_true_when_window_closes():
    window = DesktopWindow(
        handle=100,
        title="Test Application",
        process_id=1234,
        process_name="test.exe",
    )

    with (
        patch(
            "agent2_meeting_agent.desktop_controller.win32gui.IsWindow",
            side_effect=[True, False],
        ),
        patch(
            "agent2_meeting_agent.desktop_controller.win32gui.PostMessage"
        ) as mock_post_message,
        patch(
            "agent2_meeting_agent.desktop_controller.time.sleep"
        ),
    ):
        result = close_window(window)

    assert result is True

    mock_post_message.assert_called_once()


def test_close_window_returns_false_when_window_stays_open():
    window = DesktopWindow(
        handle=100,
        title="Test Application",
        process_id=1234,
        process_name="test.exe",
    )

    with (
        patch(
            "agent2_meeting_agent.desktop_controller.win32gui.IsWindow",
            return_value=True,
        ),
        patch(
            "agent2_meeting_agent.desktop_controller.win32gui.PostMessage"
        ),
        patch(
            "agent2_meeting_agent.desktop_controller.time.sleep"
        ),
    ):
        result = close_window(
            window,
            timeout_seconds=0,
        )

    assert result is False


def test_close_open_windows_returns_results():
    window = DesktopWindow(
        handle=100,
        title="Test Application",
        process_id=1234,
        process_name="test.exe",
    )

    with (
        patch(
            "agent2_meeting_agent.desktop_controller.get_open_windows",
            return_value=[window],
        ),
        patch(
            "agent2_meeting_agent.desktop_controller.close_window",
            return_value=True,
        ) as mock_close_window,
    ):
        results = close_open_windows()

    assert len(results) == 1
    assert results[0] == (window, True)

    mock_close_window.assert_called_once_with(window)


def test_open_meeting_url_success():
    with patch(
        "agent2_meeting_agent.desktop_controller.webbrowser.open",
        return_value=True,
    ) as mock_open:
        result = open_meeting_url(
            "https://meet.google.com/example"
        )

    assert result is True

    mock_open.assert_called_once_with(
        "https://meet.google.com/example",
        new=2,
    )


def test_open_meeting_url_rejects_invalid_url():
    with patch(
        "agent2_meeting_agent.desktop_controller.webbrowser.open"
    ) as mock_open:
        result = open_meeting_url("not-a-url")

    assert result is False
    mock_open.assert_not_called()


def test_open_meeting_url_rejects_empty_url():
    with patch(
        "agent2_meeting_agent.desktop_controller.webbrowser.open"
    ) as mock_open:
        result = open_meeting_url("")

    assert result is False
    mock_open.assert_not_called()