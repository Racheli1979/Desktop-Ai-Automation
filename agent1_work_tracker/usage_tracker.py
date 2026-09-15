import time
from datetime import datetime

from activity_record import ActivityRecord
from active_app import get_active_app
from idle_detector import get_idle_seconds


IDLE_TIMEOUT = 5

previous_app = None
start_time = None

idle_start_time = None
is_currently_idle = False

activity_records = []


def create_activity_record(application, start_time, end_time, status):
    duration = (end_time - start_time).total_seconds()

    record = ActivityRecord(
        date=start_time.strftime("%Y-%m-%d"),
        application=application,
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration,
        status=status
    )

    record.validate()
    return record


while True:

    current_time = datetime.now()
    idle_seconds = get_idle_seconds()

    if idle_seconds >= IDLE_TIMEOUT:

        if not is_currently_idle:

            if previous_app is not None:

                record = create_activity_record(
                    previous_app,
                    start_time,
                    current_time,
                    "Active"
                )

                activity_records.append(record)

                print(
                    f"[RECORD] {record.application} | "
                    f"{record.start_time.strftime('%H:%M:%S')} → "
                    f"{record.end_time.strftime('%H:%M:%S')} | "
                    f"{record.duration_seconds:.0f} sec | "
                    f"{record.status}"
                )

                previous_app = None
                start_time = None

            idle_start_time = current_time
            is_currently_idle = True

    else:

        if is_currently_idle:

            record = create_activity_record(
                "Idle",
                idle_start_time,
                current_time,
                "Idle"
            )

            activity_records.append(record)

            print(
                f"[RECORD] {record.application} | "
                f"{record.start_time.strftime('%H:%M:%S')} → "
                f"{record.end_time.strftime('%H:%M:%S')} | "
                f"{record.duration_seconds:.0f} sec | "
                f"{record.status}"
            )

            is_currently_idle = False
            idle_start_time = None

            previous_app = get_active_app()
            start_time = current_time

        else:

            current_app = get_active_app()

            if current_app != previous_app:

                if previous_app is not None:

                    record = create_activity_record(
                        previous_app,
                        start_time,
                        current_time,
                        "Active"
                    )

                    activity_records.append(record)

                    print(
                        f"[RECORD] {record.application} | "
                        f"{record.start_time.strftime('%H:%M:%S')} → "
                        f"{record.end_time.strftime('%H:%M:%S')} | "
                        f"{record.duration_seconds:.0f} sec | "
                        f"{record.status}"
                    )

                previous_app = current_app
                start_time = current_time

    time.sleep(5)