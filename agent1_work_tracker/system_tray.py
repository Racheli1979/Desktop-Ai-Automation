import logging
import threading

import pystray
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


def create_tray_image():
    size = 64
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.ellipse((3, 3, 61, 61), fill="#0878D1")
    draw.ellipse((9, 9, 55, 55), fill="#FFFFFF")

    draw.rounded_rectangle(
        (30, 13, 34, 19),
        radius=2,
        fill="#173B5E",
    )
    draw.rounded_rectangle(
        (13, 30, 19, 34),
        radius=2,
        fill="#173B5E",
    )

    draw.line(
        (32, 32, 22, 23),
        fill="#173B5E",
        width=4,
    )
    draw.line(
        (32, 32, 43, 22),
        fill="#173B5E",
        width=4,
    )
    draw.ellipse((28, 28, 36, 36), fill="#0878D1")

    draw.rounded_rectangle(
        (24, 43, 30, 51),
        radius=1,
        fill="#20C878",
    )
    draw.rounded_rectangle(
        (33, 38, 39, 51),
        radius=1,
        fill="#20C878",
    )
    draw.rounded_rectangle(
        (42, 32, 48, 51),
        radius=1,
        fill="#20C878",
    )

    return image


class WorkTrackerTray:
    def __init__(self, stop_event: threading.Event):
        self.stop_event = stop_event
        self.icon = pystray.Icon(
            "WorkTrackerAgent",
            create_tray_image(),
            "Work Tracker - Running",
            menu=pystray.Menu(
                pystray.MenuItem(
                    "Exit Work Tracker",
                    self._exit,
                )
            ),
        )

    def _exit(self, icon, item):
        logger.info("Exit requested from system tray")
        self.stop_event.set()
        icon.stop()

    def run(self):
        logger.info("Starting Work Tracker system tray")
        self.icon.run()

    def stop(self):
        self.icon.stop()