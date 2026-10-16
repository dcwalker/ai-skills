#!/usr/bin/env python3
"""Build this skill's eval fixtures from 2022 FIFA World Cup matches.

Usage: python3 build_fixtures.py   (needs Pillow)

Rewrites fixtures/<id>/inputs/ for every eval. Inputs mimic what a parent
collects at a game: a team app export (team-app.txt), timestamped notes
(notes.txt), team app and watch screenshots (PNG, wall clock in the status
bar), photos (JPEG with EXIF capture time), and Veo exports.

Match content is public. Wall-clock times are invented so that every event
falls mid-minute, and the expected minutes in evals.json follow from them.
"""

import json
import os
import shutil

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "fixtures")

TEAM_APP_FILE = "team-app.txt"
NOTES_FILE = "notes.txt"
HOME_GAME = "Home or Away: Home"
QATAR_OFFSET = "+03:00"
ARGENTINA_COACH = "Coach: Lionel Scaloni"

ARGENTINA = [
    (1, "Franco Armani", "GK"), (2, "Juan Foyth", "DEF"),
    (3, "Nicolás Tagliafico", "DEF"), (4, "Gonzalo Montiel", "DEF"),
    (5, "Leandro Paredes", "MID"), (6, "Germán Pezzella", "DEF"),
    (7, "Rodrigo De Paul", "MID"), (8, "Marcos Acuña", "DEF"),
    (9, "Julián Álvarez", "FWD"), (10, "Lionel Messi", "FWD"),
    (11, "Ángel Di María", "FWD"), (12, "Gerónimo Rulli", "GK"),
    (13, "Cristian Romero", "DEF"), (14, "Exequiel Palacios", "MID"),
    (15, "Ángel Correa", "FWD"), (16, "Thiago Almada", "MID"),
    (17, "Alejandro Gómez", "MID"), (18, "Guido Rodríguez", "MID"),
    (19, "Nicolás Otamendi", "DEF"), (20, "Alexis Mac Allister", "MID"),
    (21, "Paulo Dybala", "FWD"), (22, "Lautaro Martínez", "FWD"),
    (23, "Emiliano Martínez", "GK"), (24, "Enzo Fernández", "MID"),
    (25, "Lisandro Martínez", "DEF"), (26, "Nahuel Molina", "DEF"),
]

FRANCE = [
    (1, "Hugo Lloris", "GK"), (2, "Benjamin Pavard", "DEF"),
    (3, "Axel Disasi", "DEF"), (4, "Raphaël Varane", "DEF"),
    (5, "Jules Koundé", "DEF"), (6, "Mattéo Guendouzi", "MID"),
    (7, "Antoine Griezmann", "FWD"), (8, "Aurélien Tchouaméni", "MID"),
    (9, "Olivier Giroud", "FWD"), (10, "Kylian Mbappé", "FWD"),
    (11, "Ousmane Dembélé", "FWD"), (12, "Randal Kolo Muani", "FWD"),
    (13, "Youssouf Fofana", "MID"), (14, "Adrien Rabiot", "MID"),
    (15, "Jordan Veretout", "MID"), (16, "Steve Mandanda", "GK"),
    (17, "William Saliba", "DEF"), (18, "Dayot Upamecano", "DEF"),
    (20, "Kingsley Coman", "FWD"), (22, "Theo Hernández", "DEF"),
    (23, "Alphonse Areola", "GK"), (24, "Ibrahima Konaté", "DEF"),
    (25, "Eduardo Camavinga", "MID"), (26, "Marcus Thuram", "FWD"),
]


FONT_PATHS = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def font(size):
    """A font with accented Latin letters. Pillow's built-in font lacks them,
    so falling back to it would render player names wrong; stop instead."""
    for path in FONT_PATHS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise SystemExit(f"No font with accented letters found; looked for {', '.join(FONT_PATHS)}")


def roster_lines(players, with_positions=True):
    lines = ["Roster (# / Position)" if with_positions else "Roster (#)"]
    for number, name, position in players:
        lines.append(f"#{number} {name}" + (f" / {position}" if with_positions else ""))
    return lines


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text.rstrip() + "\n")


def notes_file(path, notes):
    """notes: list of (ISO timestamp with offset, text)."""
    blocks = [f"[{stamp}]\n{text}" for stamp, text in notes]
    header = "Notes export. Each note starts with its creation time.\n"
    write(path, header + "\n" + "\n\n".join(blocks))


def app_screenshot(path, status_time, clock, period, score, feed):
    """A phone screenshot of a live game tracker app."""
    image = Image.new("RGB", (590, 1280), "#f4f6f8")
    draw = ImageDraw.Draw(image)
    draw.text((40, 24), status_time, fill="black", font=font(30))
    draw.text((470, 24), "5G 82%", fill="black", font=font(24))
    draw.rectangle((0, 90, 590, 190), fill="#1f4e79")
    draw.text((40, 120), "Game Tracker", fill="white", font=font(40))
    draw.text((40, 240), score, fill="black", font=font(56))
    draw.text((40, 340), clock, fill="#1f4e79", font=font(96))
    draw.text((40, 470), period, fill="#555555", font=font(36))
    draw.text((40, 580), "Events", fill="black", font=font(36))
    y = 640
    for line in feed:
        draw.text((40, y), line, fill="black", font=font(26))
        y += 56
    image.save(path)


def watch_screenshot(path, watch_time, stopwatch):
    """An Apple Watch-style stopwatch screenshot."""
    image = Image.new("RGB", (396, 484), "black")
    draw = ImageDraw.Draw(image)
    draw.text((20, 18), "Stopwatch", fill="#ff9f0a", font=font(30))
    draw.text((300, 18), watch_time, fill="white", font=font(30))
    draw.text((30, 190), stopwatch, fill="white", font=font(72))
    draw.text((30, 400), "Lap      Stop", fill="#8e8e93", font=font(30))
    image.save(path)


def photo(path, local_time, offset, caption, color):
    """A placeholder photo whose EXIF capture time is local_time."""
    image = Image.new("RGB", (1200, 900), color)
    draw = ImageDraw.Draw(image)
    draw.text((60, 400), caption, fill="white", font=font(56))
    exif = Image.Exif()
    exif_ifd = exif.get_ifd(0x8769)
    exif_ifd[0x9003] = local_time  # DateTimeOriginal, "YYYY:MM:DD HH:MM:SS"
    if offset:
        exif_ifd[0x9011] = offset  # OffsetTimeOriginal, "+03:00"
    exif[0x0110] = "iPhone 15"  # Model
    image.save(path, "JPEG", quality=80, exif=exif)


def team_app(path, header, roster, staff, extra=()):
    lines = list(header) + [""] + roster + ["", "Staff"] + list(staff) + list(extra)
    write(path, "\n".join(lines))


def build_final(base):
    """Eval 1: the final, every kind of input, extra time and penalties."""
    team_app(
        os.path.join(base, TEAM_APP_FILE),
        [
            "Game: Argentina vs. France",
            "Date/Time: Sun, Dec 18, 2022 · 6:00 PM - 8:00 PM (AST, UTC+3)",
            "Arrival: 4:30 PM",
            "Location: Lusail Stadium",
            "Address: Lusail Stadium, Lusail, Qatar",
            "Opponent: France",
            HOME_GAME,
            ("Notes: FIFA World Cup Qatar 2022 Final. Competition page: "
            "https://www.fifa.com/en/tournaments/mens/worldcup/qatar2022"),
            "Result: T 3-3",
        ],
        roster_lines(ARGENTINA),
        [ARGENTINA_COACH],
    )
    write(
        os.path.join(base, "france-roster.txt"),
        "\n".join(["France squad, copied from the federation site"] + roster_lines(FRANCE)
                  + ["", "Coach: Didier Deschamps"]),
    )
    notes_file(os.path.join(base, NOTES_FILE), [
        ("2022-12-18 17:45:10 +03:00",
         ("Starting XI Argentina: 23 E. Martínez; 26 Molina, 13 Romero, 19 Otamendi, "
         "3 Tagliafico; 7 De Paul, 24 Enzo Fernández, 20 Mac Allister; 10 Messi, "
         "9 Álvarez, 11 Di María\n"
         "Starting XI France: 1 Lloris; 5 Koundé, 4 Varane, 18 Upamecano, "
         "22 T. Hernández; 8 Tchouaméni, 14 Rabiot, 7 Griezmann; 11 Dembélé, "
         "9 Giroud, 10 Mbappé")),
        ("2022-12-18 17:58:05 +03:00",
         ("YouTube stream for the family back home started at 17:58:00: "
         "https://www.youtube.com/watch?v=WCF2022demo (title: Argentina vs. France)")),
        ("2022-12-18 18:00:20 +03:00", "Kickoff!"),
        ("2022-12-18 18:35:50 +03:00", "GOAL Di María! Mac Allister set him up. 2-0"),
        ("2022-12-18 18:40:50 +03:00",
         "France double sub: Thuram on for Giroud, Kolo Muani on for Dembélé"),
        ("2022-12-18 18:52:50 +03:00", "HT 2-0"),
        ("2022-12-18 19:08:10 +03:00", "Second half underway"),
        ("2022-12-18 19:17:40 +03:00", "Yellow for Rabiot (foul on De Paul)"),
        ("2022-12-18 19:26:40 +03:00", "Acuña on for Di María"),
        ("2022-12-18 19:33:40 +03:00",
         "France: Coman on for Griezmann, Camavinga on for Theo Hernández"),
        ("2022-12-18 19:43:55 +03:00", "MBAPPÉ AGAIN 2-2!!! volley, Thuram assist"),
        ("2022-12-18 19:49:40 +03:00", "Yellow Thuram, diving"),
        ("2022-12-18 20:00:40 +03:00", "Full time 2-2, extra time coming"),
        ("2022-12-18 20:06:00 +03:00", "Extra time underway"),
        ("2022-12-18 20:06:30 +03:00", "Montiel on for Molina"),
        ("2022-12-18 20:17:30 +03:00", "Paredes on for De Paul"),
        ("2022-12-18 20:21:30 +03:00", "ET halftime"),
        ("2022-12-18 20:23:00 +03:00", "Second period of ET underway"),
        ("2022-12-18 20:25:30 +03:00", "MESSI 3-2!!"),
        ("2022-12-18 20:35:30 +03:00",
         "Montiel handball, Mbappé scores the pen 3-3, hat trick"),
        ("2022-12-18 20:38:30 +03:00", "Dybala on for Tagliafico"),
        ("2022-12-18 20:40:30 +03:00", "End of extra time 3-3. Penalties!"),
        ("2022-12-18 20:55:00 +03:00",
         ("Pens: Mbappé scored, Messi scored, Coman saved by E. Martínez, Dybala "
         "scored, Tchouaméni missed wide, Paredes scored, Kolo Muani scored, "
         "Montiel scored. ARGENTINA WIN 4-2 ON PENS")),
        ("2022-12-18 21:30:00 +03:00",
         ("Observations: France had no shot on target until the 70th minute. "
         "Thuram and Kolo Muani changed the game. Emiliano Martínez's save on "
         "Kolo Muani in the last minute of extra time kept Argentina alive.")),
    ])
    shots = os.path.join(base, "screenshots")
    os.makedirs(shots)
    app_screenshot(os.path.join(shots, "IMG_4112.PNG"), "6:23", "22:41", "1st Half",
                   "ARG 1 - 0 FRA", ["23'  Goal (PK) - L. Messi #10 (ARG)"])
    watch_screenshot(os.path.join(shots, "IMG_4119.PNG"), "7:20", "12:05.80")
    app_screenshot(os.path.join(shots, "IMG_4127.PNG"), "7:43", "80:12", "2nd Half",
                   "ARG 2 - 1 FRA", ["80'  Goal (PK) - K. Mbappé #10 (FRA)",
                                     "71'  Sub (FRA) - Coman ON, Griezmann OFF"])
    watch_screenshot(os.path.join(shots, "IMG_4130.PNG"), "8:10", "04:21.37")
    photos = os.path.join(base, "photos")
    os.makedirs(photos)
    photo(os.path.join(photos, "IMG_4101.jpg"), "2022:12:18 17:48:12", QATAR_OFFSET,
          "Teams walking out", "#3a6ea5")
    photo(os.path.join(photos, "IMG_4133.jpg"), "2022:12:18 20:25:44", QATAR_OFFSET,
          "Messi celebrating his goal", "#2e8b57")
    photo(os.path.join(photos, "IMG_4170.jpg"), "2022:12:18 21:20:05", QATAR_OFFSET,
          "Trophy lift", "#b8860b")


def build_mexico(base):
    """Eval 2: no anchor at all for the second half."""
    team_app(
        os.path.join(base, TEAM_APP_FILE),
        [
            "Game: Argentina vs. Mexico",
            "Date/Time: Sat, Nov 26, 2022 · 10:00 PM - 12:00 AM (AST, UTC+3)",
            "Location: Lusail Stadium",
            "Address: Lusail Stadium, Lusail, Qatar",
            "Opponent: Mexico",
            HOME_GAME,
            ("Notes: FIFA World Cup Qatar 2022, Group C. Competition page: "
            "https://www.fifa.com/en/tournaments/mens/worldcup/qatar2022"),
            "Result: W 2-0",
        ],
        roster_lines(ARGENTINA),
        [ARGENTINA_COACH],
    )
    notes_file(os.path.join(base, NOTES_FILE), [
        ("2022-11-26 22:00:15 +03:00", "Kickoff"),
        ("2022-11-26 22:47:40 +03:00", "HT 0-0, pretty flat"),
        ("2022-11-26 23:22:20 +03:00",
         "MESSI from outside the box!!! Di María assist. 1-0"),
        ("2022-11-26 23:45:10 +03:00", "Enzo curler, 2-0. Mac Allister assist"),
        ("2022-11-26 23:54:00 +03:00", "Full time 2-0"),
    ])


def build_poland(base):
    """Eval 3: substitute coach, no opponent roster, a saved penalty, a photo."""
    team_app(
        os.path.join(base, TEAM_APP_FILE),
        [
            "Game: Poland vs. Argentina",
            "Date/Time: Wed, Nov 30, 2022 · 10:00 PM - 12:00 AM (AST, UTC+3)",
            "Location: Stadium 974",
            "Address: Stadium 974, Ras Abu Aboud, Doha, Qatar",
            "Opponent: Poland",
            "Home or Away: Away",
            ("Notes: FIFA World Cup Qatar 2022, Group C. Competition page: "
            "https://www.fifa.com/en/tournaments/mens/worldcup/qatar2022"),
            "Result: W 2-0",
        ],
        roster_lines(ARGENTINA),
        [ARGENTINA_COACH],
    )
    notes_file(os.path.join(base, NOTES_FILE), [
        ("2022-11-30 21:30:00 +03:00",
         ("Scaloni is out sick today, Pablo Aimar is running the team. "
          "Dybala is away too")),
        ("2022-11-30 22:00:10 +03:00", "Kickoff"),
        ("2022-11-30 22:38:40 +03:00", "Messi penalty SAVED by Szczęsny"),
        ("2022-11-30 22:50:20 +03:00", "Halftime 0-0"),
        ("2022-11-30 23:03:00 +03:00", "2nd half go"),
        ("2022-11-30 23:03:40 +03:00", "GOAL Mac Allister! Molina cross. 1-0"),
        ("2022-11-30 23:24:30 +03:00", "Julián Álvarez 2-0, Enzo assist"),
        ("2022-11-30 23:53:30 +03:00", "FT 2-0"),
    ])
    photos = os.path.join(base, "photos")
    os.makedirs(photos)
    photo(os.path.join(photos, "IMG_5001.jpg"), "2022:11:30 22:51:02", QATAR_OFFSET,
          "Halftime huddle", "#3a6ea5")


def build_australia(base):
    """Eval 4: club tournament, period length and halftime unknown."""
    team_app(
        os.path.join(base, TEAM_APP_FILE),
        [
            "Game: France vs. Australia",
            "Date/Time: Sat, Oct 10, 2026 · 10:00 AM (PDT, UTC-7)",
            "Location: Riverside Fields, Field 3",
            "Address: 100 Example Way, Springfield",
            "Opponent: Australia",
            HOME_GAME,
            ("Notes: Fall World Cup Tournament, Pool B. Every team in the "
            "tournament is named after a World Cup country."),
            "Result: W 4-1",
        ],
        roster_lines(FRANCE, with_positions=False),
        ["Coach: Didier Deschamps"],
    )
    notes_file(os.path.join(base, NOTES_FILE), [
        ("2026-10-10 10:00:05 -07:00", "Kickoff"),
        ("2026-10-10 10:08:50 -07:00", "Australia score first, Goodwin. 0-1"),
        ("2026-10-10 10:27:00 -07:00", "Rabiot header 1-1, Theo cross"),
        ("2026-10-10 10:32:10 -07:00", "Giroud 2-1, Rabiot assist"),
        ("2026-10-10 11:13:30 -07:00", "Mbappé header 3-1, Dembélé cross"),
        ("2026-10-10 11:16:40 -07:00", "Giroud again 4-1, Mbappé assist"),
    ])


def build_saudi(base):
    """Eval 5: Veo's AI tags credit a goal to the wrong team."""
    team_app(
        os.path.join(base, TEAM_APP_FILE),
        [
            "Club schedule export (Sprocket)",
            "TUE 22 NOV GAME",
            "Argentina vs Saudi Arabia",
            "1:00 PM - 3:00PM (AST, UTC+3)",
            "Lusail Stadium",
            "Lusail Stadium, Lusail, Qatar",
            "Game Type: Home",
            "Opponent: Saudi Arabia",
            ("Competition: FIFA World Cup Qatar 2022, Group C "
            "(https://www.fifa.com/en/tournaments/mens/worldcup/qatar2022)"),
            "L (1-2)",
        ],
        roster_lines(ARGENTINA, with_positions=False),
        ["Lionel Scaloni, Head Coach"],
    )
    write(os.path.join(base, "veo-match.json"), json.dumps({
        "slug": "20221122-argentina-vs-saudi-arabia-example",
        "title": "Argentina vs. Saudi Arabia",
        "start": "2022-11-22T12:55:00+03:00",
        "end": "2022-11-22T15:05:00+03:00",
        "duration": 7800,
        "own_team_home_or_away": "home",
        "opponent_team_name": "Saudi Arabia",
        "info": {"stats": {"score_aggregated": {"own": 2, "opponent": 1}}},
    }, indent=2))
    write(os.path.join(base, "veo-periods.json"), json.dumps([
        {"timeframe": [300, 3310], "duration": 3010, "is_confirmed": False},
        {"timeframe": [4500, 7630], "duration": 3130, "is_confirmed": False},
    ], indent=2))
    events_panel = [
        "Copied from the Veo Events panel",
        "1ST PERIOD",
        "1’ · ARG · AI · Kickoff",
        "10’ · ARG · AI · Goal · 1 - 0",
        "11’ · KSA · AI · Kickoff",
        "2ND PERIOD",
        "46’ · KSA · AI · Kickoff",
        "48’ · ARG · AI · Goal · 2 - 0",
        "49’ · KSA · AI · Kickoff",
        "53’ · KSA · AI · Goal · 2 - 1",
        "54’ · ARG · AI · Kickoff",
    ]
    write(os.path.join(base, "veo-events.txt"), "\n".join(events_panel))
    notes_file(os.path.join(base, NOTES_FILE), [
        ("2022-11-22 13:09:31 +03:00", "Messi pen 1-0"),
        ("2022-11-22 14:12:30 +03:00", "Al-Shehri equalizes?! 1-1"),
        ("2022-11-22 14:17:30 +03:00", "Al-Dawsari screamer. 1-2. Stunned."),
    ])


MOROCCO = [
    (1, "Yassine Bounou", "GK"), (2, "Achraf Hakimi", "DEF"),
    (3, "Noussair Mazraoui", "DEF"), (4, "Sofyan Amrabat", "MID"),
    (5, "Nayef Aguerd", "DEF"), (6, "Romain Saïss", "DEF"),
    (7, "Hakim Ziyech", "FWD"), (8, "Azzedine Ounahi", "MID"),
    (9, "Abderrazak Hamdallah", "FWD"), (11, "Abdelhamid Sabiri", "MID"),
    (12, "Munir Mohamedi", "GK"), (15, "Selim Amallah", "MID"),
    (16, "Abde Ezzalzouli", "FWD"), (17, "Sofiane Boufal", "FWD"),
    (18, "Jawad El Yamiq", "DEF"), (19, "Youssef En-Nesyri", "FWD"),
    (20, "Achraf Dari", "DEF"), (21, "Walid Cheddira", "FWD"),
    (22, "Ahmed Reda Tagnaouti", "GK"), (25, "Yahia Attiyat Allah", "DEF"),
]


def journal_export(base, zone, offset_hours, entries):
    """A journal-app JSON export: one entry per note, UTC times, a zone name,
    Markdown-escaped text, and photos stored by MD5 with no EXIF offset.

    entries: list of (local "YYYY-MM-DD HH:MM:SS", text or None, photo caption
    or None). An entry with a caption holds only that photo.
    """
    import datetime
    import hashlib

    folder = os.path.join(base, "notes-export")
    photos = os.path.join(folder, "photos")
    os.makedirs(photos)
    local_zone = datetime.timezone(datetime.timedelta(hours=offset_hours))
    out = []
    for index, (local, text, caption) in enumerate(entries):
        moment = datetime.datetime.strptime(local, "%Y-%m-%d %H:%M:%S").replace(tzinfo=local_zone)
        utc = moment.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = {"uuid": f"{index + 1:032X}", "creationDate": utc, "timeZone": zone}
        if caption:
            temp = os.path.join(photos, "tmp.jpeg")
            photo(temp, moment.strftime("%Y:%m:%d %H:%M:%S"), None, caption,
                  "#2e8b57" if index % 2 else "#3a6ea5")
            with open(temp, "rb") as handle:
                # Journal exports name photos by MD5; this is a file name, not security.
                digest = hashlib.md5(handle.read(), usedforsecurity=False).hexdigest()
            os.rename(temp, os.path.join(photos, f"{digest}.jpeg"))
            moment_id = f"{index + 101:032X}"
            entry["text"] = f"![](journal-moment://{moment_id})"
            entry["photos"] = [{"identifier": moment_id, "md5": digest,
                                "type": "jpeg", "date": utc}]
        else:
            entry["text"] = text
        out.append(entry)
    write(os.path.join(folder, "Journal.json"),
          json.dumps({"metadata": {"version": "1.0"}, "entries": out},
                     indent=2, ensure_ascii=False))


def build_portugal(base):
    """Eval 6: a journal export like real sideline notes: written minutes,
    first names, us and them, an unsure scorer, a one-sided substitution, a
    written minute the tracker corrects, one it cannot, and a post-match card.
    """
    team_app(
        os.path.join(base, TEAM_APP_FILE),
        [
            "Game: Morocco vs. Portugal",
            "Date/Time: Sat, Dec 10, 2022 · 6:00 PM - 8:00 PM (AST, UTC+3)",
            "Location: Al Thumama Stadium",
            "Address: Al Thumama Stadium, Doha, Qatar",
            "Opponent: Portugal",
            HOME_GAME,
            ("Notes: FIFA World Cup Qatar 2022, Quarter-final. Competition page: "
            "https://www.fifa.com/en/tournaments/mens/worldcup/qatar2022"),
            "Result: W 1-0",
        ],
        roster_lines(MOROCCO),
        ["Coach: Walid Regragui"],
    )
    journal_export(base, "Asia/Qatar", 3, [
        ("2022-12-10 17:47:10", None, "Warmups"),
        ("2022-12-10 18:05:00", "5’ yellow on them, hacked down Hakimi", None),
        ("2022-12-10 18:32:05", None, "Hakimi on the ball"),
        ("2022-12-10 18:42:10", "42’ GOAL 1\\-0 Youssef? header, Yahia cross", None),
        ("2022-12-10 18:49:05", "HT 1\\-0", None),
        ("2022-12-10 19:03:05", "2nd half", None),
        ("2022-12-10 19:20:40", "64’ yellow on them", None),
        ("2022-12-10 19:33:30", "77’ Walid in", None),
        ("2022-12-10 19:49:20", "90\\+2 yellow Walid", None),
        ("2022-12-10 19:50:40", "90\\+3 second yellow Walid\\. Down to 10", None),
        ("2022-12-10 19:55:20", "FT\\!\\!\\! 1\\-0 semis", None),
        ("2022-12-10 20:05:00",
         "Apparently Coach Regragui got a yellow after the game\\.", None),
    ])
    shots = os.path.join(base, "screenshots")
    os.makedirs(shots)
    app_screenshot(os.path.join(shots, "IMG_7311.PNG"), "7:21", "63:12", "2nd Half",
                   "MAR 1 - 0 POR", ["63'  Yellow Card (POR)",
                                     "42'  Goal - MAR"])


BUILDERS = {
    1: build_final,
    2: build_mexico,
    3: build_poland,
    4: build_australia,
    5: build_saudi,
    6: build_portugal,
}


def main():
    for eval_id, build in BUILDERS.items():
        base = os.path.join(FIXTURES, str(eval_id), "inputs")
        shutil.rmtree(base, ignore_errors=True)
        os.makedirs(base)
        build(base)
        print(f"fixtures/{eval_id}/inputs: {sorted(os.listdir(base))}")


if __name__ == "__main__":
    main()
