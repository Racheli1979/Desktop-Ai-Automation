import time
from datetime import datetime

from active_app import get_active_app
from idle_detector import get_idle_seconds


IDLE_TIMEOUT = 5

previous_app = None
start_time = None

idle_start_time = None
is_currently_idle = False


while True:

    current_time = datetime.now()
    idle_seconds = get_idle_seconds()

    if idle_seconds >= IDLE_TIMEOUT:

        if not is_currently_idle:

            if previous_app is not None:

                duration = current_time - start_time

                print(
                    f"{previous_app}: "
                    f"{start_time.strftime('%H:%M:%S')} → "
                    f"{current_time.strftime('%H:%M:%S')} "
                    f"({duration.total_seconds():.0f} seconds)"
                )

                previous_app = None
                start_time = None

            idle_start_time = current_time
            is_currently_idle = True

            print(
                f"Started: Idle "
                f"at {idle_start_time.strftime('%H:%M:%S')}"
            )

    else:

        if is_currently_idle:

            print(
                f"Idle: "
                f"{idle_start_time.strftime('%H:%M:%S')} → "
                f"{current_time.strftime('%H:%M:%S')} "
                f"({(current_time - idle_start_time).total_seconds():.0f} seconds)"
            )

            is_currently_idle = False
            idle_start_time = None

            current_app = get_active_app()

            previous_app = current_app
            start_time = current_time

            print(
                f"Started: {current_app} "
                f"at {start_time.strftime('%H:%M:%S')}"
            )

        else:

            current_app = get_active_app()

            if current_app != previous_app:

                if previous_app is not None:

                    duration = current_time - start_time

                    print(
                        f"{previous_app}: "
                        f"{start_time.strftime('%H:%M:%S')} → "
                        f"{current_time.strftime('%H:%M:%S')} "
                        f"({duration.total_seconds():.0f} seconds)"
                    )

                previous_app = current_app
                start_time = current_time

                print(
                    f"Started: {current_app} "
                    f"at {start_time.strftime('%H:%M:%S')}"
                )

    time.sleep(5)