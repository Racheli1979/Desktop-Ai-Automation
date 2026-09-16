from datetime import datetime
from pathlib import Path
from zipfile import BadZipFile

from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from activity_record import ActivityRecord


EXCEL_FILE = Path(__file__).parent / "work_hours.xlsx"

HEADERS = [
    "Date",
    "Application",
    "Start",
    "End",
    "Duration",
]


def create_excel_file() -> None:
    workbook = Workbook()

    sheet = workbook.active
    sheet.title = "Work Hours"

    sheet.append(HEADERS)

    workbook.save(EXCEL_FILE)


def load_or_create_workbook():
    if not EXCEL_FILE.exists():
        create_excel_file()

    try:
        return load_workbook(EXCEL_FILE)

    except (
        BadZipFile,
        InvalidFileException,
        OSError,
        ValueError,
    ):
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_file = EXCEL_FILE.with_name(
            f"work_hours_corrupted_{timestamp}.xlsx"
        )

        EXCEL_FILE.rename(backup_file)

        print(
            "Corrupted Excel file backed up to: "
            f"{backup_file.name}"
        )

        create_excel_file()

        return load_workbook(EXCEL_FILE)


def update_daily_totals(workbook) -> None:
    activity_sheet = workbook["Work Hours"]

    totals: dict[str, float] = {}

    for row in activity_sheet.iter_rows(
        min_row=2,
        values_only=True,
    ):
        date = row[0]
        application = row[1]
        duration = row[4]

        if not date or not application or duration is None:
            continue

        if application == "Idle":
            continue

        totals[date] = totals.get(date, 0) + duration

    if "Daily Totals" in workbook.sheetnames:
        totals_sheet = workbook["Daily Totals"]

        if totals_sheet.max_row:
            totals_sheet.delete_rows(
                1,
                totals_sheet.max_row,
            )
    else:
        totals_sheet = workbook.create_sheet(
            "Daily Totals"
        )

    totals_sheet.append([
        "Date",
        "Total Work Seconds",
    ])

    for date, total in sorted(totals.items()):
        totals_sheet.append([
            date,
            round(total),
        ])


def save_activity_record(record: ActivityRecord) -> None:
    workbook = load_or_create_workbook()
    sheet = workbook["Work Hours"]

    sheet.append([
        record.date,
        record.application,
        record.start_time.strftime("%H:%M:%S"),
        record.end_time.strftime("%H:%M:%S"),
        round(record.duration_seconds),
    ])

    update_daily_totals(workbook)

    workbook.save(EXCEL_FILE)


if __name__ == "__main__":
    if not EXCEL_FILE.exists():
        create_excel_file()

    print(f"Excel file is ready: {EXCEL_FILE}")