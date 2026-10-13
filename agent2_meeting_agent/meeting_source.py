import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .meeting import Meeting


PROJECT_DIR = Path(__file__).resolve().parent.parent
MCP_TOOL_NAME = "list_events"
MAX_RESULTS = 2500


def _parse_datetime(value: str) -> datetime:
    """Convert an ISO datetime string to local naive datetime."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone().replace(tzinfo=None)

    return parsed


async def _fetch_events() -> list[dict]:
    """Fetch calendar events through the MCP server."""
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.calendar_mcp_server"],
        cwd=str(PROJECT_DIR),
    )

    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            result = await session.call_tool(
                MCP_TOOL_NAME,
                {"max_results": MAX_RESULTS},
            )

            if result.isError:
                error_details = "\n".join(
                    item.text
                    for item in result.content
                    if hasattr(item, "text")
                )
                raise RuntimeError(
                    f"MCP tool '{MCP_TOOL_NAME}' returned an error: "
                    f"{error_details}"
                )

            events = []

            for item in result.content:
                if not hasattr(item, "text"):
                    continue

                try:
                    data = json.loads(item.text)
                except json.JSONDecodeError as exc:
                    raise RuntimeError(
                        "MCP server returned invalid JSON."
                    ) from exc

                if isinstance(data, list):
                    events.extend(
                        event for event in data
                        if isinstance(event, dict)
                    )
                elif isinstance(data, dict):
                    events.append(data)

            return events


def get_meetings() -> list[Meeting]:
    """Return timed Google Calendar events as Meeting objects."""
    events = asyncio.run(_fetch_events())
    meetings = []

    for event in events:
        start_value = event.get("start")
        end_value = event.get("end")

        # Skip all-day events, which have dates but no times.
        if (
            not isinstance(start_value, str)
            or not isinstance(end_value, str)
            or "T" not in start_value
            or "T" not in end_value
        ):
            continue

        try:
            start_time = _parse_datetime(start_value)
            end_time = _parse_datetime(end_value)
        except ValueError:
            continue

        duration_seconds = (end_time - start_time).total_seconds()

        if duration_seconds <= 0:
            continue

        duration_minutes = int(duration_seconds / 60)

        if duration_minutes <= 0:
            continue

        meeting = Meeting(
            title=event.get("title") or "(No title)",
            start_time=start_time,
            duration_minutes=duration_minutes,
            participants=event.get("participants") or [],
            description=event.get("description") or "",
            meeting_url=event.get("meeting_url"),
        )

        meeting.validate()
        meetings.append(meeting)

    return meetings