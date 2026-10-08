#!/usr/bin/env python3
"""Eval-only fake Google Calendar MCP server.

A real, protocol-compliant stdio MCP server (built on the official `mcp`
SDK) implementing the read side of the Google Calendar connector that a
meeting-notes skill calls: list_events, search_events, get_event, and
list_calendars. See common.py's module docstring for the general stub-server
design.

Schema fidelity note: every tool's parameters were copied from the live
connector's schema. The event objects and the list_events, get_event, and
search_events envelopes were copied from live responses (issue #96, a test
event created, read back, and deleted):

  list_events    {"accessRole": "owner", "events": [...], "summary": "<calendar>",
                  "timeZone": "<IANA>", "updated": "<ISO>"}
  search_events  {"events": [...]}
  get_event      <one event object>
  event          {"conferenceData": {}, "created", "creator": {"email", "self"},
                  "description", "end": {"dateTime", "timeZone"}, "eventType",
                  "htmlLink", "id", "location", "organizer": {"email", "self"},
                  "start": {"dateTime", "timeZone"}, "status", "summary",
                  "updated", "useDefaultReminders", "attendees": [...]}

Unverified, and worth knowing before trusting a diff:

- `attendees` entries follow the connector schema's Attendee definition
  (email, displayName, responseStatus, organizer, self, optionalAttendee);
  the live test event had none, so their rendering was not observed.
- list_calendars' layout follows the Calendar API's CalendarList resource
  (id, summary, primary, timeZone, accessRole) and was not called live.
- search_events is semantic live. The stub matches events containing every
  query word in the title, description, location, or attendees, which is
  stricter, so a fixture should name its events in words a search would use.
- No paging: every page holds all matches, and no `nextPageToken` is sent.

Environment: MCP_STUB_STATE_FILE / MCP_STUB_STATE_OUT / MCP_STUB_LOG, same
contract as trello_stub.py.

State model:
  {
    "calendar": {"id": "user@example.com", "summary": "Dan",
                 "timeZone": "America/Los_Angeles"},
    "updated": "<ISO datetime>",
    "stub_now": "<ISO datetime, optional: the default startTime>",
    "events": [<event objects as above>]
  }
"""

import datetime

from common import StubState

state = StubState(default={"calendar": {}, "events": []})

from mcp.server.mcpserver import MCPServer  # noqa: E402

server = MCPServer("calendar-stub")


def _parse(value: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))


def _now() -> datetime.datetime:
    now = state.data.get("stub_now")
    return _parse(now) if now else datetime.datetime.now(datetime.timezone.utc)


def _event_text(event: dict) -> str:
    people = " ".join(f"{a.get('email', '')} {a.get('displayName', '')}"
                      for a in event.get("attendees", []))
    return " ".join((event.get("summary", ""), event.get("description", ""),
                     event.get("location", ""), people)).lower()


def _all_words(event: dict, text: str) -> bool:
    haystack = _event_text(event)
    return all(word in haystack for word in text.lower().split())


@server.tool()
def list_events(
    calendarId: str = "",  # NOSONAR(S107) the live tool's schema
    startTime: str = "",
    endTime: str = "",
    fullText: str = "",
    orderBy: str = "",
    pageSize: int = 100,
    pageToken: str = "",
    eventType: list[str] | None = None,
    timeZone: str = "",
) -> dict:
    """Returns events on the given calendar matching all specified
    constraints. startTime defaults to now and endTime to startTime plus 7
    days. fullText matches title, description, location, or attendees."""
    start = _parse(startTime) if startTime else _now()
    end = _parse(endTime) if endTime else start + datetime.timedelta(days=7)
    events = [e for e in state.data["events"]
              if _parse(e["end"]["dateTime"]) > start and _parse(e["start"]["dateTime"]) < end
              and (not fullText or _all_words(e, fullText))]
    if orderBy in ("startTime", "startTimeDesc"):
        events.sort(key=lambda e: _parse(e["start"]["dateTime"]), reverse=orderBy == "startTimeDesc")
    calendar = state.data["calendar"]
    result = {"accessRole": "owner", "events": events[:max(1, min(pageSize, 250))],
              "summary": calendar.get("summary", ""), "timeZone": calendar.get("timeZone", ""),
              "updated": state.data.get("updated", "")}
    state.log_call("list_events", {"calendarId": calendarId, "startTime": startTime,
                                   "endTime": endTime, "fullText": fullText,
                                   "orderBy": orderBy, "pageSize": pageSize}, result)
    return result


@server.tool()
def search_events(query: str, pageSize: int = 0, pageToken: str = "") -> dict:
    """Searches events on the user's primary calendar."""
    events = [e for e in state.data["events"] if _all_words(e, query)]
    if pageSize:
        events = events[:pageSize]
    result = {"events": events}
    state.log_call("search_events", {"query": query, "pageSize": pageSize}, result)
    return result


@server.tool()
def get_event(eventId: str, calendarId: str = "") -> dict:
    """Returns a single event on the given calendar."""
    event = next((e for e in state.data["events"] if e["id"] == eventId), None)
    if event is None:
        raise ValueError(f"calendar-stub: no event with id {eventId!r}")
    state.log_call("get_event", {"eventId": eventId, "calendarId": calendarId}, event)
    return event


@server.tool()
def list_calendars(pageSize: int = 100, pageToken: str = "") -> dict:
    """Returns the calendars this user has access to."""
    calendar = state.data["calendar"]
    result = {"items": [{"id": calendar.get("id", ""), "summary": calendar.get("summary", ""),
                         "primary": True, "timeZone": calendar.get("timeZone", ""),
                         "accessRole": "owner"}]}
    state.log_call("list_calendars", {"pageSize": pageSize}, result)
    return result


if __name__ == "__main__":
    server.run(transport="stdio")
