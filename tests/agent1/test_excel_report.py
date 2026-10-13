from datetime import datetime

from openpyxl import load_workbook

from agent1_work_tracker import excel_report
from agent1_work_tracker.activity_record import ActivityRecord


def create_record(
    application,
    start_minute,
    end_minute,
    duration,
    status="Active",
):
    return ActivityRecord(
        date="2026-09-17",
        application=application,
        start_time=datetime(
            2026,
            9,
            17,
            10,
            start_minute,
            0,
        ),
        end_time=datetime(
            2026,
            9,
            17,
            10,
            end_minute,
            0,
        ),
        duration_seconds=duration,
        status=status,
    )


def test_create_excel_file(tmp_path, monkeypatch):
    excel_file = tmp_path / "work_hours.xlsx"

    monkeypatch.setattr(
        excel_report,
        "EXCEL_FILE",
        excel_file,
    )

    excel_report.create_excel_file()

    assert excel_file.exists()

    workbook = load_workbook(excel_file)

    assert "Work Hours" in workbook.sheetnames

    sheet = workbook["Work Hours"]

    headers = [
        sheet.cell(1, column).value
        for column in range(1, 6)
    ]

    assert headers == [
        "Date",
        "Application",
        "Start",
        "End",
        "Duration",
    ]


def test_save_activity_record(tmp_path, monkeypatch):
    excel_file = tmp_path / "work_hours.xlsx"

    monkeypatch.setattr(
        excel_report,
        "EXCEL_FILE",
        excel_file,
    )

    record = create_record(
        application="Visual Studio Code",
        start_minute=0,
        end_minute=10,
        duration=10,
    )

    excel_report.save_activity_record(record)

    workbook = load_workbook(excel_file)
    sheet = workbook["Work Hours"]

    assert sheet.cell(2, 1).value == "2026-09-17"
    assert (
        sheet.cell(2, 2).value
        == "Visual Studio Code"
    )
    assert sheet.cell(2, 5).value == 10


def test_previous_records_are_preserved(
    tmp_path,
    monkeypatch,
):
    excel_file = tmp_path / "work_hours.xlsx"

    monkeypatch.setattr(
        excel_report,
        "EXCEL_FILE",
        excel_file,
    )

    first_record = create_record(
        application="Visual Studio Code",
        start_minute=0,
        end_minute=10,
        duration=10,
    )

    second_record = create_record(
        application="Google Chrome",
        start_minute=10,
        end_minute=20,
        duration=10,
    )

    excel_report.save_activity_record(first_record)
    excel_report.save_activity_record(second_record)

    workbook = load_workbook(excel_file)
    sheet = workbook["Work Hours"]

    assert sheet.max_row == 3

    assert (
        sheet.cell(2, 2).value
        == "Visual Studio Code"
    )

    assert (
        sheet.cell(3, 2).value
        == "Google Chrome"
    )


def test_idle_is_excluded_from_daily_total(
    tmp_path,
    monkeypatch,
):
    excel_file = tmp_path / "work_hours.xlsx"

    monkeypatch.setattr(
        excel_report,
        "EXCEL_FILE",
        excel_file,
    )

    active_record = create_record(
        application="Visual Studio Code",
        start_minute=0,
        end_minute=10,
        duration=10,
        status="Active",
    )

    idle_record = create_record(
        application="Idle",
        start_minute=10,
        end_minute=20,
        duration=10,
        status="Idle",
    )

    excel_report.save_activity_record(
        active_record
    )

    excel_report.save_activity_record(
        idle_record
    )

    workbook = load_workbook(excel_file)

    sheet = workbook["Daily Totals"]

    assert sheet.cell(2, 1).value == "2026-09-17"
    assert sheet.cell(2, 2).value == 10