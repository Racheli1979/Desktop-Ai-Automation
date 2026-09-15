import time
from datetime import datetime, timedelta

from activity_record import ActivityRecord
from active_app import get_active_app
from idle_detector import get_idle_seconds, get_last_input_time
from excel_report import save_activity_record


# Final application behavior:
# consider the user idle only after 5 minutes
# without keyboard or mouse input.
IDLE_TIMEOUT = 300

# Check the active application 5 times per second.
# This helps capture short application sessions.
CHECK_INTERVAL = 0.2


previous_app = None
start_time = None

idle_start_time = None
is_currently_idle = False


def create_activity_record(application, start_time, end_time, status):
    """
    Create and validate an activity record.

    Timestamps are normalized to whole seconds so that
    Start, End and Duration remain consistent in Excel.
    """

    start_time = start_time.replace(microsecond=0)
    end_time = end_time.replace(microsecond=0)

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


def save_and_print_record(record):
    """
    Save the activity record to Excel and print it.
    """

    # Do not save zero-duration records
    if record.duration_seconds <= 0:
        return

    save_activity_record(record)

    print(
        f"[RECORD] {record.application} | "
        f"{record.start_time.strftime('%H:%M:%S')} → "
        f"{record.end_time.strftime('%H:%M:%S')} | "
        f"{record.duration_seconds:.0f} sec | "
        f"{record.status}"
    )


while True:

    current_time = datetime.now()
    idle_seconds = get_idle_seconds()

    # ---------------------------------------------------------
    # USER BECOMES IDLE
    # ---------------------------------------------------------
    if idle_seconds >= IDLE_TIMEOUT:

        if not is_currently_idle:

            # Idle officially starts when the timeout is reached,
            # not when the last input occurred.
            idle_start_time = current_time - timedelta(
                seconds=idle_seconds - IDLE_TIMEOUT
            )

            # Close the current application activity record.
            if previous_app is not None and start_time is not None:

                record = create_activity_record(
                    previous_app,
                    start_time,
                    idle_start_time,
                    "Active"
                )

                save_and_print_record(record)

                previous_app = None
                start_time = None

            is_currently_idle = True

    # ---------------------------------------------------------
    # USER IS NOT IDLE
    # ---------------------------------------------------------
    else:

        # -----------------------------------------------------
        # USER RETURNS FROM IDLE
        # -----------------------------------------------------
        if is_currently_idle:

            # The user's actual last input marks the end of Idle.
            idle_end_time = get_last_input_time()

            record = create_activity_record(
                "Idle",
                idle_start_time,
                idle_end_time,
                "Idle"
            )

            save_and_print_record(record)

            is_currently_idle = False
            idle_start_time = None

            # Start tracking the application that is currently
            # active after the user returns.
            previous_app = get_active_app()
            start_time = idle_end_time

        # -----------------------------------------------------
        # NORMAL ACTIVE TRACKING
        # -----------------------------------------------------
        else:

            current_app = get_active_app()

            # First detected application
            if previous_app is None:

                previous_app = current_app
                start_time = current_time

            # Application changed
            elif current_app != previous_app:

                # Close previous application record.
                if start_time is not None:

                    record = create_activity_record(
                        previous_app,
                        start_time,
                        current_time,
                        "Active"
                    )

                    save_and_print_record(record)

                # Start tracking the new application.
                previous_app = current_app
                start_time = current_time

    time.sleep(CHECK_INTERVAL)