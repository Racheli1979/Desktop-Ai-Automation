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


def _get_mcp_server_command() -> tuple[str, list[str], str]:
    if getattr(sys, "frozen", False):
        server_exe = Path(sys.executable).with_name(
            "CalendarMcpServer.exe"
        )

        if not server_exe.is_file():
            raise FileNotFoundError(
                f"MCP server executable not found: {server_exe}"
            )

        return str(server_exe), [], str(server_exe.parent)

    return (
        sys.executable,
        ["-m", "mcp_server.calendar_mcp_server"],
        str(PROJECT_DIR),
    )


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone().replace(tzinfo=None)

    return parsed


async def _fetch_events() -> list[dict]:
    command, args, cwd = _get_mcp_server_command()

    server = StdioServerParameters(
        command=command,
        args=args,
        cwd=cwd,
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
    events = asyncio.run(_fetch_events())
    meetings = []

    for event in events:
        start_value = event.get("start")
        end_value = event.get("end")

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