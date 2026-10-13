from datetime import datetime

from agent1_work_tracker import usage_tracker


def test_create_record():
    tracker = usage_tracker.ActivityTracker()

    start = datetime(
        2026,
        9,
        17,
        10,
        0,
        0,
        500000,
    )

    end = datetime(
        2026,
        9,
        17,
        10,
        0,
        10,
        500000,
    )

    record = tracker.create_record(
        application="Visual Studio Code",
        start_time=start,
        end_time=end,
        status="Active",
    )

    assert record.application == "Visual Studio Code"
    assert record.duration_seconds == 10
    assert record.start_time.microsecond == 0
    assert record.end_time.microsecond == 0


def test_start_tracking():
    tracker = usage_tracker.ActivityTracker()

    start = datetime(
        2026,
        9,
        17,
        10,
        0,
        0,
    )

    tracker.start_tracking(
        "Visual Studio Code",
        start,
    )

    assert tracker.current_app == "Visual Studio Code"
    assert tracker.activity_start == start


def test_stop_tracking_saves_record(
    monkeypatch,
):
    tracker = usage_tracker.ActivityTracker()

    start = datetime(
        2026,
        9,
        17,
        10,
        0,
        0,
    )

    end = datetime(
        2026,
        9,
        17,
        10,
        0,
        10,
    )

    saved_records = []

    monkeypatch.setattr(
        usage_tracker,
        "save_activity_record",
        lambda record: saved_records.append(record),
    )

    tracker.start_tracking(
        "Visual Studio Code",
        start,
    )

    tracker.stop_tracking(end)

    assert len(saved_records) == 1

    assert (
        saved_records[0].application
        == "Visual Studio Code"
    )

    assert saved_records[0].duration_seconds == 10

    assert tracker.current_app is None
    assert tracker.activity_start is None


def test_zero_duration_is_not_saved(
    monkeypatch,
):
    tracker = usage_tracker.ActivityTracker()

    start = datetime(
        2026,
        9,
        17,
        10,
        0,
        0,
    )

    saved_records = []

    monkeypatch.setattr(
        usage_tracker,
        "save_activity_record",
        lambda record: saved_records.append(record),
    )

    tracker.save_record(
        application="Visual Studio Code",
        start_time=start,
        end_time=start,
        status="Active",
    )

    assert saved_records == []


def test_application_change(
    monkeypatch,
):
    tracker = usage_tracker.ActivityTracker()

    start = datetime(
        2026,
        9,
        17,
        10,
        0,
        0,
    )

    change_time = datetime(
        2026,
        9,
        17,
        10,
        0,
        10,
    )

    saved_records = []

    monkeypatch.setattr(
        usage_tracker,
        "save_activity_record",
        lambda record: saved_records.append(record),
    )

    tracker.start_tracking(
        "Visual Studio Code",
        start,
    )

    monkeypatch.setattr(
        usage_tracker,
        "get_active_app",
        lambda: "Google Chrome",
    )

    tracker.update_application(change_time)

    assert len(saved_records) == 1

    assert (
        saved_records[0].application
        == "Visual Studio Code"
    )

    assert saved_records[0].duration_seconds == 10

    assert tracker.current_app == "Google Chrome"
    assert tracker.activity_start == change_time


def test_start_idle_closes_active_session(
    monkeypatch,
):
    tracker = usage_tracker.ActivityTracker(
        idle_timeout=5
    )

    start = datetime(
        2026,
        9,
        17,
        10,
        0,
        0,
    )

    current_time = datetime(
        2026,
        9,
        17,
        10,
        0,
        10,
    )

    saved_records = []

    monkeypatch.setattr(
        usage_tracker,
        "save_activity_record",
        lambda record: saved_records.append(record),
    )

    tracker.start_tracking(
        "Visual Studio Code",
        start,
    )

    tracker.start_idle(
        current_time,
        idle_seconds=10,
    )

    assert len(saved_records) == 1

    assert (
        saved_records[0].application
        == "Visual Studio Code"
    )

    assert saved_records[0].duration_seconds == 5

    assert tracker.is_idle is True
    assert tracker.current_app is None
    assert tracker.activity_start is None