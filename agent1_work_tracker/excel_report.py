from datetime import datetime
from pathlib import Path
import logging
import shutil
from zipfile import BadZipFile

from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from .activity_record import ActivityRecord


logger = logging.getLogger(__name__)


# Store runtime data outside the PyInstaller application files.
BASE_DIR = Path.home() / "DesktopAiAutomation"
EXCEL_FILE = BASE_DIR / "work_hours.xlsx"


def create_excel_file() -> None:
    """
    Create the Excel workbook if it does not exist.
    """

    BASE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    workbook = Workbook()

    work_sheet = workbook.active
    work_sheet.title = "Work Hours"

    work_sheet.append(
        [
            "Date",
            "Application",
            "Start",
            "End",
            "Duration",
        ]
    )

    totals_sheet = workbook.create_sheet(
        "Daily Totals"
    )

    totals_sheet.append(
        [
            "Date",
            "Total Work Seconds",
        ]
    )

    workbook.save(EXCEL_FILE)

    logger.info(
        "Excel file created: %s",
        EXCEL_FILE,
    )


def backup_corrupted_file() -> None:
    """
    Create a backup of a corrupted Excel file before replacing it.
    """

    if not EXCEL_FILE.exists():
        return

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_file = (
        EXCEL_FILE.parent
        / f"work_hours_corrupted_{timestamp}.xlsx"
    )

    shutil.copy2(
        EXCEL_FILE,
        backup_file,
    )

    logger.warning(
        "Corrupted Excel file backed up to: %s",
        backup_file,
    )


def load_or_create_workbook():
    """
    Load the existing workbook or create a new one.
    """

    BASE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

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
        logger.exception(
            "Excel file is corrupted or cannot be opened: %s",
            EXCEL_FILE,
        )

        backup_corrupted_file()

        create_excel_file()

        return load_workbook(EXCEL_FILE)


def update_daily_totals(workbook) -> None:
    """
    Recalculate daily work totals from non-idle records.
    """

    if "Work Hours" not in workbook.sheetnames:
        return

    if "Daily Totals" in workbook.sheetnames:
        totals_sheet = workbook["Daily Totals"]

        totals_sheet.delete_rows(
            1,
            totals_sheet.max_row,
        )

    else:
        totals_sheet = workbook.create_sheet(
            "Daily Totals"
        )

    totals_sheet.append(
        [
            "Date",
            "Total Work Seconds",
        ]
    )

    totals = {}

    work_sheet = workbook["Work Hours"]

    for row in work_sheet.iter_rows(
        min_row=2,
        values_only=True,
    ):
        if not row:
            continue

        date = row[0]
        duration = row[4]

        if date is None or duration is None:
            continue

        application = row[1]

        if application == "Idle":
            continue

        totals[date] = (
            totals.get(date, 0)
            + float(duration)
        )

    for date, total_seconds in sorted(
        totals.items(),
        key=lambda item: str(item[0]),
    ):
        totals_sheet.append(
            [
                date,
                total_seconds,
            ]
        )


def save_activity_record(
    record: ActivityRecord,
) -> None:
    """
    Save an activity record to the Excel workbook.
    """

    try:
        workbook = load_or_create_workbook()

        work_sheet = workbook["Work Hours"]

        work_sheet.append(
            [
                record.date,
                record.application,
                record.start_time.strftime(
                    "%H:%M:%S"
                ),
                record.end_time.strftime(
                    "%H:%M:%S"
                ),
                record.duration_seconds,
            ]
        )

        update_daily_totals(workbook)

        workbook.save(EXCEL_FILE)

        logger.info(
            "Activity record saved: %s | %.0f sec | %s",
            record.application,
            record.duration_seconds,
            record.status,
        )

    except (
        OSError,
        PermissionError,
        ValueError,
    ):
        logger.exception(
            "Failed to save activity record: %s",
            record.application,
        )
        raise