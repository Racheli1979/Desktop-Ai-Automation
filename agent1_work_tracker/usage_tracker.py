import time
from datetime import datetime

from active_app import get_active_app


previous_app = None
start_time = None


while True:
    current_app = get_active_app()
    current_time = datetime.now()

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