#!/usr/bin/env python3
"""Time and date arithmetic for meeting notes, so it is never done by hand.

Subcommands:

  check-end  Does start + duration match the stated end? (Step 2)
    meeting_times.py check-end --start "2026-10-28 14:00" --duration 30 --end "14:30"
    Prints the computed end and whether it matches. --end takes "HH:MM",
    "H:MM AM/PM", or a full "YYYY-MM-DD HH:MM".

  window     A meeting window in every form a source search needs. (Step 1b)
    meeting_times.py window --start "2026-10-28 14:00" --end "2026-10-28 14:45" \\
        --tz America/Los_Angeles [--extend-end 15]
    Prints, as JSON: the local start and end, Unix timestamps (Slack's
    after/before and oldest/latest), UTC times as "YYYY-MM-DD HH:MM"
    (Confluence CQL), the local date for a date filter (on:YYYY-MM-DD),
    and, with --extend-end, the end pushed later by that many minutes.

  due        The calendar date a weekday due date refers to. (Step 7)
    meeting_times.py due --meeting-date 2026-10-28 --weekday friday [--next-week]
    Prints the first such weekday after the meeting date (with --next-week,
    the one in the following week). When the weekday is the meeting's own,
    it says so: "Friday" said on a Friday may mean that day or a week later.

Times are local to --tz (an IANA name such as America/Los_Angeles); a
daylight-saving change inside the window is handled. Standard library only
(Python 3.9+).
"""

import argparse
import datetime
import json
import re
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def parse_datetime(value, base_date=None):
    """A "YYYY-MM-DD HH:MM" value, or a bare time on base_date."""
    value = value.strip()
    match = re.match(r"^(\d{4}-\d{2}-\d{2})[ T](.+)$", value)
    if match:
        base_date = datetime.date.fromisoformat(match.group(1))
        value = match.group(2)
    if base_date is None:
        raise ValueError(f"{value!r} needs a date (YYYY-MM-DD HH:MM)")
    clock = re.match(r"^(\d{1,2}):(\d{2})(?::\d{2})?\s*([AaPp][Mm])?$", value)
    if not clock:
        raise ValueError(f"cannot read the time {value!r}")
    hour, minute, meridiem = int(clock.group(1)), int(clock.group(2)), clock.group(3)
    if meridiem:
        if not 1 <= hour <= 12:
            raise ValueError(f"{value!r}: hour must be 1-12 with AM/PM")
        hour = hour % 12 + (12 if meridiem.lower() == "pm" else 0)
    return datetime.datetime.combine(base_date, datetime.time(hour, minute))


def zone(name):
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        sys.exit(f"meeting_times: unknown time zone {name!r}")


def fmt_clock(moment):
    return moment.strftime("%I:%M %p").lstrip("0")


def check_end(args):
    start = parse_datetime(args.start)
    computed = start + datetime.timedelta(minutes=args.duration)
    stated = parse_datetime(args.end, start.date())
    if stated < start:  # an end past midnight
        stated += datetime.timedelta(days=1)
    result = {
        "start": start.strftime("%Y-%m-%d %H:%M"),
        "duration_minutes": args.duration,
        "computed_end": computed.strftime("%Y-%m-%d %H:%M"),
        "computed_end_display": fmt_clock(computed),
        "stated_end": stated.strftime("%Y-%m-%d %H:%M"),
        "matches": computed == stated,
        "difference_minutes": int((stated - computed).total_seconds() // 60),
    }
    print(json.dumps(result, indent=2))


def window(args):
    tz = zone(args.tz)
    start = parse_datetime(args.start).replace(tzinfo=tz)
    end = parse_datetime(args.end, start.date()).replace(tzinfo=tz)
    if end <= start:
        end += datetime.timedelta(days=1)
    utc = datetime.timezone.utc

    def forms(moment):
        return {
            "local": moment.strftime("%Y-%m-%d %H:%M %Z"),
            "unix": int(moment.timestamp()),
            "utc": moment.astimezone(utc).strftime("%Y-%m-%d %H:%M"),
        }

    result = {"time_zone": args.tz, "start": forms(start), "end": forms(end)}
    dates = sorted({start.date().isoformat(), end.date().isoformat()})
    result["local_dates"] = dates
    if args.extend_end:
        result["extended_end"] = forms(end + datetime.timedelta(minutes=args.extend_end))
    print(json.dumps(result, indent=2))


def due(args):
    meeting = datetime.date.fromisoformat(args.meeting_date)
    target = WEEKDAYS.index(args.weekday.lower())
    ahead = (target - meeting.weekday()) % 7 or 7
    if args.next_week:
        ahead += 7
    date = meeting + datetime.timedelta(days=ahead)
    result = {
        "meeting_date": meeting.isoformat(),
        "meeting_weekday": WEEKDAYS[meeting.weekday()].capitalize(),
        "due_date": date.isoformat(),
        "due_display": f"{date.strftime('%b')} {date.day}, {date.year}",
    }
    if target == meeting.weekday() and not args.next_week:
        result["note"] = ("The meeting is on this weekday, so it may mean the meeting day "
                          "itself or a week later. Check the transcript or ask.")
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=__doc__.split("\n\n", 1)[1])
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("check-end", help="start + duration against the stated end")
    p.add_argument("--start", required=True, help='"YYYY-MM-DD HH:MM"')
    p.add_argument("--duration", required=True, type=int, help="minutes")
    p.add_argument("--end", required=True, help='"HH:MM", "H:MM PM", or "YYYY-MM-DD HH:MM"')
    p.set_defaults(func=check_end)

    p = sub.add_parser("window", help="a meeting window as timestamps and UTC times")
    p.add_argument("--start", required=True, help='"YYYY-MM-DD HH:MM" local time')
    p.add_argument("--end", required=True, help='"HH:MM" or "YYYY-MM-DD HH:MM" local time')
    p.add_argument("--tz", required=True, help="IANA time zone, e.g. America/Los_Angeles")
    p.add_argument("--extend-end", type=int, default=0, help="minutes to add after the end")
    p.set_defaults(func=window)

    p = sub.add_parser("due", help="the date a weekday due date refers to")
    p.add_argument("--meeting-date", required=True, help="YYYY-MM-DD")
    p.add_argument("--weekday", required=True, choices=WEEKDAYS + [d.capitalize() for d in WEEKDAYS])
    p.add_argument("--next-week", action="store_true", help='for "next <weekday>" meaning the following week')
    p.set_defaults(func=due)

    args = parser.parse_args()
    try:
        args.func(args)
    except ValueError as error:
        sys.exit(f"meeting_times: {error}")


if __name__ == "__main__":
    main()
