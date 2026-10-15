---
name: build-soccer-scoresheet
description: Build a Markdown match report (scoresheet) for a soccer game from whatever the user has, such as team app screenshots (Sprocket, TeamSnap, Demosphere), watch stopwatch screenshots, timestamped notes, photos, and recordings (Veo, YouTube). Correlates wall-clock times with the game clock into an accurate timeline of goals, cards, substitutions, and other significant events in standard minute notation (33', 45+2', 90+3', 105+1'), and fills match details, rosters, and coaches from the team app, calendar, email, and the web. Use whenever the user wants a scoresheet, match report, game recap, game summary, or timeline of a soccer or football match, including youth and club games, even if they just hand over screenshots and notes and say "write up the game".
metadata:
  category: utilities
---

# Build Soccer Scoresheet

Turn the scraps a parent or fan collects during a game into one match report:
when each goal, card, and substitution happened, who was on each roster, and
where the recording is. The hard part is time. Most inputs carry a wall-clock
time (a phone status bar, a note's creation time, a photo's EXIF data), while
the report needs the game minute, so the skill builds a per-period mapping
between the two and converts every event through it.

Never invent anything: no scorer, minute, quote, or observation that is not in
the inputs or a source the user confirmed. A gap is filled by looking it up,
by asking, or by saying plainly that it is missing.

## Sources

Work from roles, not products. A match usually has one source per role, and
each product's quirks live in its own reference file; read the one that
applies before using it.

| Role | What it supplies | Trust | Products |
|------|------------------|-------|----------|
| Team app | Date, kickoff time, venue and field, opponent, home or away, final result, roster with jersey numbers (sometimes positions), coaching staff | The official result | Sprocket ([references/sprocket.md](references/sprocket.md)), TeamSnap ([references/teamsnap.md](references/teamsnap.md)), Demosphere (no reference yet; read the pages as shown) |
| Video platform | Recording link, recording start time, period boundaries, timed events (often AI-tagged) | Timing is good; team and event attribution is unconfirmed | Veo ([references/veo.md](references/veo.md)), YouTube and other links |
| User's inputs | Screenshots, notes, photos, pasted links | Scorers, cards, substitutions, starters, observations | Phone and watch screenshots, notes apps, camera roll |
| Calendar | Venue, address, kickoff time | Lower than the team app | Any calendar the session can read |
| Email | Coach's post-match notes, recording links, competition details | As written | Any mail the session can read |
| Web | Competition page, opponent roster, venue address | Confirm before use | Search |

When two sources disagree, the team app's result wins over the video
platform's tags, and the user's notes win over AI tags for who did what.
Report every disagreement to the user rather than resolving it silently.

## Step 1: Inventory the inputs

Open every file the user provided and list what each one contributes. Look
at images yourself; do not rely on file names. Tell screenshots from photos:
a screenshot (a status bar, an app or watch screen) is only a source to read
data from, such as the time, the game clock, the score, or who scored and
assisted, and it never appears in the report. Photos of the game do.

- **Team app screenshots** (Sprocket, TeamSnap, Demosphere game trackers):
  the status-bar time (wall clock, minutes only), the game clock (with
  seconds) and period label, the score, and any event list with minutes,
  scorers, and assists.
- **Watch stopwatch screenshots**: the watch's time of day (minutes only) and
  the stopwatch reading, which is elapsed time in the current period.
- **Notes**: from any notes or journal app, usually one short entry per
  event, as a text file, a JSON export, or a pasted list. Take each entry's
  creation time (with its time zone; exports often store UTC plus a zone
  name) and its text. A note is written just after the event, so treat its
  time as the event time unless the note says otherwise ("goal at 18:22",
  "2 min ago"). Exports may escape Markdown (`1\-0`, `\.`); read and quote
  the unescaped text. Photos attached to an entry take the entry's time
  unless they carry their own.
- **Minutes the user wrote**: many notes start with a minute read off a
  watch (`50' 2-0`). Keep it next to the note's timestamp. It is an anchor
  (Step 3) and a cross-check (Step 4), good to about a minute.
- **Photos**: the capture time from EXIF `DateTimeOriginal` plus
  `OffsetTimeOriginal`. Run `python3 scripts/photo_time.py <photo>...`
  (standard library only, resolved relative to this `SKILL.md`), or use
  `exiftool` or `mdls` if you prefer. The script reads only under the
  user's home and `$TMPDIR`; if it refuses a photo, copy the photos into a
  working folder under home (`mktemp -d ~/scoresheet.XXXX`) rather than
  changing `TMPDIR`. Exported photos often lose the
  offset; then the time is local, in the zone of the notes or the match. A
  photo may show an event (a celebration, a substitution board) or just the
  day. Keep every photo for the report.
- **Links**: recordings, team app pages, competition pages.

Record the time zone of every wall-clock source. Phone, watch, notes, and
photos normally share the user's local time zone, but a photo's EXIF offset
or a note's stated zone overrides that assumption.

## Step 2: Identify the match and fill gaps

Settle these before converting any times: date, home and away teams, which
team is the user's, kickoff time with time zone, venue, competition, final
result, both rosters, and the coaches.

For anything the inputs lack, look it up, in this order: the team app, the
video platform, the calendar, email (search for the opponent, the date, or
"recording", "video", "Veo"), then the web. Read the matching reference file
for how to reach a product's data. Then confirm what you found with the user
in one message, naming the source of each item, before writing the report.
Skip the confirmation only for details the user handed you directly.

Coaching staff come from the team app's staff list, whatever their title
there. If the notes say someone else coached this game, show the regular
coach struck through, followed by the substitute (see the template).

Starters are rarely recorded anywhere. Label players Starter or Substitute
only when the notes (or another input) name the starting lineup.

If something the template needs is still missing after the lookups, ask for
it. If the user says it is unavailable, the report says so (see the
template); never guess.

## Step 3: Anchor wall-clock time to the game clock

The game clock does not stop in soccer, so within one period, wall-clock time
and elapsed game time differ by a constant. Each period has its own constant,
because halftime and breaks reset it. Find each period's kickoff in wall-clock
time from its anchors:

- A note that marks the period's start ("Kickoff", "Second half underway")
  gives the kickoff directly, to the second.
- A screenshot showing wall clock W and game clock G in that period gives
  kickoff = W − G. The status bar shows minutes only, so this places kickoff
  in a 60-second window: [W:00 − G, W:59 − G]. Game trackers often run a
  continuous clock, so `80:12` in the second half of 2×45 is 35:12 into the
  period; use the period label and the score to tell which it is.
- A recording's start time plus the video platform's period boundaries give
  the kickoff to the second (see the video platform's reference).
- A note with a written minute M, created at T, places kickoff in a window
  of about a minute (T minus M−1 to M minutes of elapsed play, adjusted for
  the period). With no kickoff note, intersect the windows from every
  written minute in the period; a written minute that does not fit the
  others is the one to doubt, not the kickoff.

Combine every anchor for a period and keep the intersection of their windows.
If anchors for one period disagree by more than a minute, stop and show the
user the conflicting inputs.

**Period length.** Club and youth games vary (2×25, 2×30, 2×35, 2×40, 2×45,
extra-time periods of 5 to 15 minutes), so derive the length from the match
itself: halftime and full-time markers, the stopwatch at the halftime
whistle, the video platform's period durations, or the competition rules. If
the evidence does not settle it, ask the user for the period length before
converting any minutes. Do not assume 45 minutes.

**Missing anchor.** If a period has no anchor, estimate its kickoff from what
is known (the previous period's end plus a typical break, a scheduled
restart, the full-time time minus the period length plus visible stoppage),
mark every minute that depends on it as estimated, and ask the user to
confirm the estimate before you write the final report. Show the draft
minutes with the question so the user can judge them.

## Step 4: Convert each event to a game minute

For an event at wall-clock time T in a period that kicked off at K, with
elapsed time e = T − K, regular period length D, and S the minutes played
before the period (0 for the first half, D for the second, 2D for the first
extra-time period, and so on):

- **Within regular time** (e < D): minute = S + floor(e / 60) + 1, written
  `33'`. An event at 32:15 elapsed is in the 33rd minute; one at 0:30 is in
  the 1st.
- **In stoppage time** (e ≥ D): added = floor((e − D) / 60) + 1, written
  `(S + D)+added'`. 45:00 plus 1:30 is `45+2'`; 90:00 plus 2:10 is `90+3'`.
- **Continuous clock**: the second half continues from the first. In 2×45,
  ten minutes after the restart is `55'`, not `10'`; in 2×30 it is `40'`.
- **Extra time** continues the same way: with 15-minute periods, the first
  starts at `91'` and ends at `105+N'`, the second starts at `106'` and ends
  at `120+N'`.
- **Penalty shootout** kicks have no minute. List them in kick order after
  the end of extra time.

Video platforms often number minutes continuously without stoppage notation
(Veo shows `61'` for the first minute of second-half stoppage in 2×30).
Recompute every minute from the period boundaries rather than copying the
platform's number.

**When sources disagree on a minute** (the minute the user wrote, the
minute computed from the timestamp, a team app or tracker screenshot, the
video platform's event time), compare every source that covers the event
and use the minute they support. A tracker screenshot or a recording time
outranks a written minute, which is read off a watch by eye. If the sources
still disagree, or the only two disagree, show the user the candidates and
the evidence for each and ask which is right; do not pick one silently.

Choose the period by comparing T with each period's kickoff and end. An
event between periods (a halftime substitution, a card after the whistle)
takes the minute of the whistle that ended the period before it, or the
first minute of the next period if the note says it took effect at the
restart.

## Step 5: Collect the significant events

Log every significant event the inputs support, including:

- goals (with assists), penalty goals, own goals
- penalties missed or saved
- yellow cards, second yellows, red cards, with the reason when known
- substitutions
- kickoff, halftime, second-half kickoff, end of regulation, extra-time
  periods, the shootout, and the end of the game
- injuries, VAR decisions, abandoned or suspended play, and anything else
  the notes treat as significant

Merge duplicates: the same goal can appear in a team app screenshot, a note,
a photo, and the video's event list. Use the most precise time and the most
specific description, and cross-check the running score after every goal
against the screenshots and the final result. If the scores do not add up,
or a goal is tagged to the wrong team by the video platform, tell the user
what disagrees and which source you followed.

Notes are shorthand. Resolve them against the rosters:

- First names, nicknames, and misspellings ("Pirce") map to the roster
  player they clearly mean; write the full roster name and number. If two
  players fit, ask.
- "Us", "we", "them", and "they" become the team's name. The report never
  says us or them.
- A question mark ("Goal Youssef?") means the user was unsure. Keep the
  name and append ` (unconfirmed)` to that event, and list it in your reply.
- When the player is unknown, write the team instead of inventing a name:
  `Goal: Poland (scorer unknown)`, `Yellow Card: Portugal (player unknown)`.
- A substitution with only one side known keeps the template shape and
  drops the unknown part: `Substitution: Walid Cheddira #21 ↑ ON`, unless
  the recording fills it in (below).

**Fill gaps from the recording.** When an event is missing a player (the
player going off in a substitution, the player booked, the scorer) and a
recording is available, look at it. Open the recording in the browser at the
event's offset (event wall-clock time minus recording start, or the video
platform's event link), pause, and step through the 30 seconds before and
after, taking screenshots and zooming on the players near the touchline, the
substitution board, or the referee. Fill the gap only when a jersey number is
clearly legible and matches a roster player; append ` (from video)` to that
event and tell the user which frames you used. If nothing is legible, leave
the gap and say you checked. Never download the video to do this without
asking the user first.
- Incidents the user thought worth noting (a hard foul with no call, an
  injury) are events too: `- **74'** - Incident: ...`, in the user's terms.
- Events after the final whistle (a card shown to a coach after the game)
  go after the Game over line, with **Post-match** in place of a minute.

## Step 6: Write the report

Fill this template exactly, in this order. Square-bracketed text is replaced;
everything else stays as written.

```markdown
# Match Report: [Home Team] vs. [Away Team]

## Match Details

- **Date:** YYYY-MM-DD
- **Start Time:** HH:MM [time zone abbreviation] (UTC±H)
- **Venue:** [Stadium or park name, field if known, address]
- **Competition:** [Competition name](link)

## Rosters

### [Home Team]

- **#1 Firstname Lastname** (GK) - Starter
- **#4 Firstname Lastname** (DEF) - Starter
- **#12 Firstname Lastname** (GK) - Substitute
- **Coach:** Firstname Lastname

### [Away Team]

- **#1 Firstname Lastname** (GK) - Starter
- **Coach:** Firstname Lastname

## Significant Events

- **1'** - Kickoff
- **32'** - Goal: [Player Name] #[Number] (Assisted by [Player Name] #[Number])
- **45+2'** - Yellow Card: [Player Name] #[Number] (Tactical foul)
- **68'** - Substitution: [Player Name] #[Number] ↑ ON, [Player Name] #[Number] ↓ OFF
- **90+2'** - Game over ([Home Team] [score]-[score] [Away Team])

## Match Observations

[The user's tactical notes, key moments, and thoughts on the match]

## Post-Match Commentary

[Quotes and insights from the coach's post-match talk, interview, or email]

## Recording

[[Platform] | [Recording title]](link)
```

**Match Details**

- Start Time is the scheduled kickoff in 24-hour time with the match's local
  time zone, for example `18:00 AST (UTC+3)` or `10:50 PDT (UTC-7)`.
- Venue includes the field when the team app names one.
- Competition links to the league, tournament, or event page. Without a link,
  write the name alone and say in your reply that no link was found.

**Rosters**

- One line per player, sorted by jersey number. Starters come before
  substitutes when starters are known; each group is sorted by number.
- Add the position (GK, DEF, MID, FWD) only when a source records it, mapping
  detailed positions (center back is DEF, winger is FWD). Omit the
  parentheses otherwise.
- Add ` - Starter` or ` - Substitute` only when the starting lineup is known.
- A player without a known number is written without the `#`.
- The coach line comes last. A substitute coach is written
  `- **Coach:** ~~Regular Coach~~ Substitute Coach`. List other staff
  (assistant coach, team manager) on their own lines with their role.
- With no roster for a team, the section holds the line `No opponent roster`
  (or `No roster` for the user's own team).

**Significant Events**

- One line per event in chronological order, minute in bold.
- Players are written `Name #Number`, for example `Lionel Messi #10`.
- Event wording: `Goal`, `Goal (penalty)`, `Own goal`, `Penalty missed`
  (with `saved by Name #N` when known), `Yellow Card`, `Second Yellow Card`,
  `Red Card`, `Substitution`, `Kickoff`, `Halftime`, `Second half kickoff`,
  `End of regulation`, `Extra time kickoff`, `Extra time halftime`,
  `End of extra time`, `Game over`, `Incident`. Put a card's reason in
  parentheses when known. Cards and incidents after the final whistle use
  **Post-match** in place of a minute, after the Game over line.
- Estimated minutes, only in a draft the user has not yet confirmed, end in
  `(est.)`.
- Shootout kicks use **Pens** in place of a minute, one line per kick in
  order: `- **Pens** - Kick 1: Kylian Mbappé #10 (France) scored`. The final
  line is `- **Pens** - Game over ([Home Team] [score]-[score] [Away Team],
  [Winner] win [x]-[y] on penalties)`.
- **Photos** go inline, in chronological order with the events. A photo that
  shows an event goes on the line after that event, indented two spaces:
  `  ![Short description](path/to/photo.jpg)`. Other photos get their own
  line at their minute (`- **52'** - Photo`), or `**Pre-match**` and
  `**Post-match**` in place of the minute, with the image indented below.
  Use paths relative to where the report will be saved. Screenshots (app,
  tracker, watch, or video frames) are sources only; never embed them or
  give them a line.
- **Video links**: when an event's moment in the recording can be linked,
  append ` ([video](link))` to its line. YouTube supports a `t=<seconds>`
  parameter (`?t=` on a bare URL, `&t=` when the URL already has `?v=`),
  where seconds = event wall-clock time − recording start time. Veo's event
  links are described in [references/veo.md](references/veo.md). Never guess
  a timestamp link format; without a documented or verified one, leave the
  link off.

**Empty sections.** Every section stays in the report. When there is nothing
for it, write a short plain statement instead: `No observations`, `No notes`,
`No opponent roster`, `No recording`.

**Recording.** One line per recording: `[Platform | Recording title](link)`,
for example `[Veo | Home Team vs. Away Team](https://app.veo.co/matches/...)`.
Recording links come from links the user pasted, the notes, the team app, or
email.

## Step 7: Deliver

Show the user the finished Markdown. If they already said where it goes (a
file path, a journal, a document), put it there; otherwise ask. Along with
it, list briefly:

- what you looked up and from where
- any estimate, disagreement between sources, or event you could not place
- anything left out because no source had it
