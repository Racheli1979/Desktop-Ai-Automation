import time
from datetime import datetime, timedelta

from activity_record import ActivityRecord
from active_app import get_active_app
from excel_report import save_activity_record
from idle_detector import get_idle_seconds, get_last_input_time


IDLE_TIMEOUT = 300
CHECK_INTERVAL = 0.2


class ActivityTracker:

    def __init__(
        self,
        idle_timeout: int = IDLE_TIMEOUT,
        check_interval: float = CHECK_INTERVAL,
    ):
        self.idle_timeout = idle_timeout
        self.check_interval = check_interval

        self.current_app = None
        self.activity_start = None
        self.idle_start = None
        self.is_idle = False

    def create_record(
        self,
        application,
        start_time,
        end_time,
        status,
    ):
        start_time = start_time.replace(microsecond=0)
        end_time = end_time.replace(microsecond=0)

        record = ActivityRecord(
            date=start_time.strftime("%Y-%m-%d"),
            application=application,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=(end_time - start_time).total_seconds(),
            status=status,
        )

        record.validate()
        return record

    def save_record(
        self,
        application,
        start_time,
        end_time,
        status,
    ):
        record = self.create_record(
            application,
            start_time,
            end_time,
            status,
        )

        if record.duration_seconds <= 0:
            return

        save_activity_record(record)

        print(
            f"[RECORD] {record.application} | "
            f"{record.start_time:%H:%M:%S} → "
            f"{record.end_time:%H:%M:%S} | "
            f"{record.duration_seconds:.0f} sec | "
            f"{record.status}"
        )

    def start_tracking(self, application, start_time):
        self.current_app = application
        self.activity_start = start_time

    def stop_tracking(self, end_time):
        if self.current_app is None or self.activity_start is None:
            return

        self.save_record(
            self.current_app,
            self.activity_start,
            end_time,
            "Active",
        )

        self.current_app = None
        self.activity_start = None

    def start_idle(self, current_time, idle_seconds):
        self.idle_start = (
            current_time
            - timedelta(seconds=idle_seconds - self.idle_timeout)
        )

        self.stop_tracking(self.idle_start)
        self.is_idle = True

    def end_idle(self):
        if self.idle_start is None:
            self.is_idle = False
            return

        idle_end = get_last_input_time()

        self.save_record(
            "Idle",
            self.idle_start,
            idle_end,
            "Idle",
        )

        self.idle_start = None
        self.is_idle = False

        current_app = get_active_app()

        if current_app is not None:
            self.start_tracking(current_app, idle_end)

    def update_application(self, current_time):
        current_app = get_active_app()

        if current_app is None:
            return

        if self.current_app is None:
            self.start_tracking(current_app, current_time)
            return

        if current_app != self.current_app:
            self.stop_tracking(current_time)
            self.start_tracking(current_app, current_time)

    def update(self):
        current_time = datetime.now()
        idle_seconds = get_idle_seconds()

        if idle_seconds >= self.idle_timeout:
            if not self.is_idle:
                self.start_idle(current_time, idle_seconds)
            return

        if self.is_idle:
            self.end_idle()
        else:
            self.update_application(current_time)

    def run(self):
        print("Activity tracker started.")

        while True:
            try:
                self.update()
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                self.stop_tracking(datetime.now())
                print("Activity tracker stopped.")
                break

            except Exception as error:
                print(f"[ERROR] Tracker error: {error}")
                time.sleep(self.check_interval)


if __name__ == "__main__":
    ActivityTracker().run()