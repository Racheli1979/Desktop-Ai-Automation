from pathlib import Path
from datetime import datetime
from zipfile import BadZipFile

from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException


EXCEL_FILE = Path(__file__).parent / "work_hours.xlsx"

HEADERS = [
    "Date",
    "Application",
    "Start",
    "End",
    "Duration"
]


def create_excel_file():
    workbook = Workbook()

    sheet = workbook.active
    sheet.title = "Work Hours"

    sheet.append(HEADERS)

    workbook.save(EXCEL_FILE)


def load_or_create_workbook():
    """
    Load the existing Excel file or create a new one.

    If the file is corrupted, back it up and create a new file.
    """

    if not EXCEL_FILE.exists():
        create_excel_file()

    try:
        return load_workbook(EXCEL_FILE)

    except (BadZipFile, InvalidFileException, OSError, ValueError):

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_file = EXCEL_FILE.with_name(
            f"work_hours_corrupted_{timestamp}.xlsx"
        )

        EXCEL_FILE.rename(backup_file)

        print(
            f"Corrupted Excel file backed up to: "
            f"{backup_file.name}"
        )

        create_excel_file()

        return load_workbook(EXCEL_FILE)


def update_daily_totals(workbook):
    """
    Calculate total active work time for each day.

    Idle records are excluded.

    Daily totals are calculated from the same Duration
    values that are stored in the Work Hours sheet.
    """

    activity_sheet = workbook["Work Hours"]

    totals = {}

    for row in activity_sheet.iter_rows(
        min_row=2,
        values_only=True
    ):

        date = row[0]
        application = row[1]
        duration = row[4]

        # Ignore incomplete rows
        if date is None:
            continue

        if application is None:
            continue

        if duration is None:
            continue

        # Ignore Idle time
        if application == "Idle":
            continue

        totals[date] = (
            totals.get(date, 0) + duration
        )

    # Create or clear Daily Totals sheet
    if "Daily Totals" in workbook.sheetnames:

        totals_sheet = workbook["Daily Totals"]

        if totals_sheet.max_row > 0:
            totals_sheet.delete_rows(
                1,
                totals_sheet.max_row
            )

    else:

        totals_sheet = workbook.create_sheet(
            "Daily Totals"
        )

    totals_sheet.append([
        "Date",
        "Total Work Seconds"
    ])

    for date, total in sorted(totals.items()):

        totals_sheet.append([
            date,
            round(total)
        ])


def save_activity_record(record):
    """
    Add one activity record to the Excel file
    and update daily totals.
    """

    workbook = load_or_create_workbook()

    sheet = workbook["Work Hours"]

    # Normalize timestamps to whole-second precision
    # so displayed Start/End and Duration stay consistent.
    start_time = record.start_time.replace(
        microsecond=0
    )

    end_time = record.end_time.replace(
        microsecond=0
    )

    duration = round(
        (end_time - start_time).total_seconds()
    )

    sheet.append([
        record.date,
        record.application,
        start_time.strftime("%H:%M:%S"),
        end_time.strftime("%H:%M:%S"),
        duration
    ])

    update_daily_totals(workbook)

    workbook.save(EXCEL_FILE)


if __name__ == "__main__":

    if not EXCEL_FILE.exists():
        create_excel_file()

    print(
        f"Excel file is ready: {EXCEL_FILE}"
    )