import os
from pathlib import Path


APP_NAME = "DesktopAiAutomation"

LOCAL_APP_DATA = Path(
    os.getenv(
        "LOCALAPPDATA",
        str(Path.home() / "AppData" / "Local"),
    )
)

USER_DATA_DIR = LOCAL_APP_DATA / APP_NAME

EXCEL_FILE = USER_DATA_DIR / "work_hours.xlsx"

LOG_DIR = USER_DATA_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"

TOKEN_FILE = USER_DATA_DIR / "google_token.json"


def ensure_user_data_dir() -> None:
    USER_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )