import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import truststore

truststore.inject_into_ssl()

import httplib2
import google_auth_httplib2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP


APP_NAME = "DesktopAiAutomation"

PROJECT_DIR = Path(__file__).resolve().parent.parent

BUNDLE_DIR = Path(
    getattr(sys, "_MEIPASS", PROJECT_DIR)
)

CREDENTIALS_FILE = (
    BUNDLE_DIR
    / "credentials"
    / "google_oauth_client.json"
)

LOCAL_APP_DATA = Path(
    os.getenv(
        "LOCALAPPDATA",
        str(Path.home() / "AppData" / "Local"),
    )
)

USER_DATA_DIR = LOCAL_APP_DATA / APP_NAME
TOKEN_FILE = USER_DATA_DIR / "google_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly"
]

mcp = FastMCP("Google Calendar MCP Server")


def get_credentials() -> Credentials:
    USER_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    creds = None

    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(
                str(TOKEN_FILE),
                SCOPES,
            )
        except (ValueError, OSError):
            creds = None

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if not CREDENTIALS_FILE.exists():
            raise FileNotFoundError(
                "Google OAuth client configuration was not found."
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE),
            SCOPES,
        )

        creds = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(
        creds.to_json(),
        encoding="utf-8",
    )

    return creds


@mcp.tool()
def list_events(max_results: int = 250) -> list[dict]:
    if not 1 <= max_results <= 2500:
        raise ValueError(
            "max_results must be between 1 and 2500"
        )

    creds = get_credentials()

    http = httplib2.Http(timeout=30)

    authorized_http = google_auth_httplib2.AuthorizedHttp(
        creds,
        http=http,
    )

    service = build(
        "calendar",
        "v3",
        http=authorized_http,
        cache_discovery=False,
    )

    result = service.events().list(
        calendarId="primary",
        timeMin=datetime.now(timezone.utc).isoformat(),
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = []

    for event in result.get("items", []):
        start_data = event.get("start", {})
        end_data = event.get("end", {})

        start = (
            start_data.get("dateTime")
            or start_data.get("date")
        )

        end = (
            end_data.get("dateTime")
            or end_data.get("date")
        )

        if not start or not end:
            continue

        events.append(
            {
                "title": (
                    event.get("summary")
                    or "(No title)"
                ),
                "start": start,
                "end": end,
                "participants": [
                    attendee.get("displayName")
                    or attendee.get("email")
                    for attendee in event.get(
                        "attendees",
                        [],
                    )
                    if (
                        attendee.get("displayName")
                        or attendee.get("email")
                    )
                ],
                "description": (
                    event.get("description")
                    or ""
                ),
                "meeting_url": (
                    event.get("hangoutLink")
                    or next(
                        (
                            entry.get("uri")
                            for entry in event.get(
                                "conferenceData",
                                {},
                            ).get(
                                "entryPoints",
                                [],
                            )
                            if (
                                entry.get(
                                    "entryPointType"
                                )
                                == "video"
                                and entry.get("uri")
                            )
                        ),
                        None,
                    )
                ),
            }
        )

    return events


if __name__ == "__main__":
    mcp.run(transport="stdio")