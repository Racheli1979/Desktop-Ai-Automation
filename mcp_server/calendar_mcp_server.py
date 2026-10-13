
import asyncio
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


PROJECT_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = (
    PROJECT_DIR / "credentials" / "google_oauth_client.json"
)
TOKEN_FILE = PROJECT_DIR / "credentials" / "token.json"

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

mcp = FastMCP("Google Calendar MCP Server")


def get_credentials():
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_FILE), SCOPES
        )

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        if not CREDENTIALS_FILE.exists():
            raise FileNotFoundError(
                f"OAuth client file not found: {CREDENTIALS_FILE}"
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), SCOPES
        )
        creds = flow.run_local_server(port=0)

    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


@mcp.tool()
def list_events(max_results: int = 250) -> list[dict]:
    """Return upcoming events from the primary Google Calendar."""

    if not 1 <= max_results <= 2500:
        raise ValueError("max_results must be between 1 and 2500")

    creds = get_credentials()
    http = httplib2.Http(timeout=30)
    authorized_http = google_auth_httplib2.AuthorizedHttp(
        creds, http=http
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

        start = start_data.get("dateTime") or start_data.get("date")
        end = end_data.get("dateTime") or end_data.get("date")

        if not start or not end:
            continue

        events.append({
            "title": event.get("summary") or "(No title)",
            "start": start,
            "end": end,
            "participants": [
                attendee.get("displayName") or attendee.get("email")
                for attendee in event.get("attendees", [])
                if attendee.get("displayName") or attendee.get("email")
            ],
            "description": event.get("description", ""),
            "meeting_url": (
                event.get("hangoutLink")
                or next(
                    (
                        entry.get("uri")
                        for entry in event.get(
                            "conferenceData", {}
                        ).get("entryPoints", [])
                        if entry.get("entryPointType") == "video"
                        and entry.get("uri")
                    ),
                    None,
                )
            ),
        })

    return events


if __name__ == "__main__":
    mcp.run(transport="stdio")