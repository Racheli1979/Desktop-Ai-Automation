from datetime import datetime
from pathlib import Path
import logging
import shutil
from zipfile import BadZipFile

from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from .activity_record import ActivityRecord
from shared.paths import EXCEL_FILE, USER_DATA_DIR


logger = logging.getLogger(__name__)

BASE_DIR = USER_DATA_DIR


def create_excel_file() -> None:
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
            "Duration (Minutes)",
        ]
    )

    totals_sheet = workbook.create_sheet(
        "Daily Totals"
    )

    totals_sheet.append(
        [
            "Date",
            "Total Work Minutes",
            "Total Work Time",
        ]
    )

    workbook.save(EXCEL_FILE)
    workbook.close()

    logger.info(
        "Excel file created: %s",
        EXCEL_FILE,
    )


def backup_corrupted_file() -> None:
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
            "Total Work Minutes",
            "Total Work Time",
        ]
    )

    totals = {}
    work_sheet = workbook["Work Hours"]

    for row in work_sheet.iter_rows(
        min_row=2,
        values_only=True,
    ):
        if not row or len(row) < 5:
            continue

        date = row[0]
        application = row[1]
        duration_minutes = row[4]

        if date is None or duration_minutes is None:
            continue

        if application == "Idle":
            continue

        try:
            duration_minutes = float(
                duration_minutes
            )
        except (TypeError, ValueError):
            logger.warning(
                "Skipping invalid duration: %s",
                duration_minutes,
            )
            continue

        if duration_minutes < 0:
            continue

        totals[date] = (
            totals.get(date, 0.0)
            + duration_minutes
        )

    for date, total_minutes in sorted(
        totals.items(),
        key=lambda item: str(item[0]),
    ):
        total_seconds = round(
            total_minutes * 60
        )

        total_minutes_rounded = round(
            total_seconds / 60
        )

        hours, minutes = divmod(
            total_minutes_rounded,
            60,
        )

        formatted_time = (
            f"{hours} שעות ו-{minutes} דקות"
        )

        totals_sheet.append(
            [
                date,
                round(total_minutes, 2),
                formatted_time,
            ]
        )


def save_activity_record(
    record: ActivityRecord,
) -> None:
    try:
        workbook = load_or_create_workbook()

        try:
            work_sheet = workbook["Work Hours"]

            duration_minutes = (
                record.duration_seconds / 60
            )

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
                    duration_minutes,
                ]
            )

            update_daily_totals(workbook)
            workbook.save(EXCEL_FILE)

            logger.info(
                "Activity record saved: %s | %.4f minutes | %s",
                record.application,
                duration_minutes,
                record.status,
            )

        finally:
            workbook.close()

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