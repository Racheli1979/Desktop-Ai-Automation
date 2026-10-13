from datetime import datetime

import pytest

from agent1_work_tracker.activity_record import ActivityRecord


def create_valid_record():
    return ActivityRecord(
        date="2026-09-17",
        application="Visual Studio Code",
        start_time=datetime(
            2026,
            9,
            17,
            10,
            0,
            0,
        ),
        end_time=datetime(
            2026,
            9,
            17,
            10,
            0,
            10,
        ),
        duration_seconds=10,
        status="Active",
    )


def test_valid_activity_record():
    record = create_valid_record()

    record.validate()

    assert record.application == "Visual Studio Code"
    assert record.duration_seconds == 10
    assert record.status == "Active"


def test_empty_application_is_invalid():
    record = create_valid_record()
    record.application = ""

    with pytest.raises(ValueError):
        record.validate()


def test_end_time_before_start_time_is_invalid():
    record = create_valid_record()

    record.end_time = datetime(
        2026,
        9,
        17,
        9,
        59,
        59,
    )

    with pytest.raises(ValueError):
        record.validate()


def test_negative_duration_is_invalid():
    record = create_valid_record()
    record.duration_seconds = -1

    with pytest.raises(ValueError):
        record.validate()


def test_invalid_status_is_rejected():
    record = create_valid_record()
    record.status = "Unknown"

    with pytest.raises(ValueError):
        record.validate()