#!/usr/bin/env python3
"""Convert wall-clock event times to soccer game minutes.

Usage: python3 game_minutes.py < timeline.json

Reads one JSON object on stdin and prints a JSON object with every event's
minute in report notation (33', 45+2', 105+1'). Standard library only.

Input:

    {
      "recording_start": "2022-11-22T12:55:00+03:00",      (optional)
      "periods": [
        {"name": "1st half", "length_minutes": 45,
         "kickoff": "2022-11-22T13:00:00+03:00",
         "end": "2022-11-22T13:50:10+03:00"},              (end optional)
        {"name": "2nd half", "length_minutes": 45,
         "kickoff": {"recording_offset": 4500},
         "end": {"recording_offset": 7630}}
      ],
      "events": [
        {"label": "Messi penalty", "time": "2022-11-22T13:09:31+03:00"},
        {"label": "Veo goal", "time": {"recording_offset": 4650}}
      ]
    }

Every time is either an ISO 8601 timestamp with a UTC offset, or
{"recording_offset": seconds} counted from recording_start. Periods are listed
in playing order; each one's minutes continue from the lengths before it, so
the second half of 2x30 starts at 31' and extra time after 2x45 at 91'.

Output: for each period, its kickoff and, when an end is given, the minute of
the whistle that ended it. For each event, the period it falls in, the
elapsed time in that period, the minute, and seconds_to_boundary: how close
the elapsed time is to the next or previous whole minute. Events within a few
seconds of a boundary are where sources disagree; check them against other
sources before trusting the minute. An event before the first kickoff is
"Pre-match"; one after a period's end and before the next kickoff takes the
minute of that period's final whistle and is marked between_periods; one after
the last period's end is "Post-match".
"""

import datetime
import json
import sys


def parse_time(value, recording_start, what):
    if isinstance(value, dict) and "recording_offset" in value:
        if recording_start is None:
            raise ValueError(f"{what}: recording_offset needs recording_start")
        return recording_start + datetime.timedelta(seconds=float(value["recording_offset"]))
    if isinstance(value, str):
        moment = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        if moment.tzinfo is None:
            raise ValueError(f"{what}: {value!r} has no UTC offset")
        return moment
    raise ValueError(f"{what}: expected an ISO timestamp or recording_offset, got {value!r}")


def minute(elapsed, before, length):
    """Report notation for elapsed seconds into a period of length seconds."""
    if elapsed < length:
        return f"{before // 60 + int(elapsed // 60) + 1}'"
    added = int((elapsed - length) // 60) + 1
    return f"{(before + length) // 60}+{added}'"


def clock(seconds):
    sign = "-" if seconds < 0 else ""
    seconds = abs(round(seconds))
    return f"{sign}{seconds // 60}:{seconds % 60:02d}"


def build_periods(timeline, recording_start):
    """Parse the periods in playing order, with the seconds played before each."""
    periods = []
    before = 0
    for index, period in enumerate(timeline["periods"]):
        name = period.get("name", f"period {index + 1}")
        length = round(float(period["length_minutes"]) * 60)
        kickoff = parse_time(period["kickoff"], recording_start, f"{name} kickoff")
        end = parse_time(period["end"], recording_start, f"{name} end") if period.get("end") else None
        periods.append({"name": name, "kickoff": kickoff, "end": end,
                        "before": before, "length": length})
        before += length
    if not periods:
        raise ValueError("periods: at least one period with a kickoff is required")
    return periods


def describe_period(period):
    row = {"name": period["name"], "kickoff": period["kickoff"].isoformat(),
           "starts_at": f"{period['before'] // 60 + 1}'"}
    if period["end"]:
        elapsed = (period["end"] - period["kickoff"]).total_seconds()
        row["end"] = period["end"].isoformat()
        row["elapsed"] = clock(elapsed)
        row["end_minute"] = minute(elapsed, period["before"], period["length"])
    return row


def place_event(moment, periods):
    """The minute fields for an event at moment, given the parsed periods."""
    if moment < periods[0]["kickoff"]:
        return {"minute": "Pre-match"}
    current = [p for p in periods if p["kickoff"] <= moment][-1]
    if current["end"] and moment > current["end"]:
        if current is periods[-1]:
            return {"minute": "Post-match"}
        ended = (current["end"] - current["kickoff"]).total_seconds()
        return {"minute": minute(ended, current["before"], current["length"]),
                "between_periods": f"after {current['name']}"}
    elapsed = (moment - current["kickoff"]).total_seconds()
    within = elapsed % 60
    return {"period": current["name"], "elapsed": clock(elapsed),
            "minute": minute(elapsed, current["before"], current["length"]),
            "seconds_to_boundary": round(min(within, 60 - within))}


def convert(timeline):
    start = timeline.get("recording_start")
    recording_start = parse_time(start, None, "recording_start") if start else None
    periods = build_periods(timeline, recording_start)
    events = []
    for index, event in enumerate(timeline.get("events", [])):
        label = event.get("label", f"event {index + 1}")
        try:
            moment = parse_time(event.get("time"), recording_start, label)
        except ValueError as error:
            # A bad event is reported on its own row; the rest still convert.
            events.append({"label": label, "error": str(error)})
            continue
        row = {"label": label, "time": moment.isoformat()}
        row.update(place_event(moment, periods))
        events.append(row)
    return {"periods": [describe_period(p) for p in periods], "events": events}


def main():
    try:
        timeline = json.load(sys.stdin)
        result = convert(timeline)
    except (ValueError, KeyError, IndexError, TypeError) as error:
        print(json.dumps({"error": str(error)}))
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
