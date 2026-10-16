# Sprocket

Sprocket Sports hosts club websites with team schedules, results, and
rosters. A club's site is `https://<club>.sprocketsports.com`, and a team's
pages live under `/team/<team id>/program/<program id>/`. Everything useful
needs the user to be signed in; signed out, the pages redirect to the club's
public homepage, and the roster page shows "Public view of roster is
currently disabled". Sign-in happens on `login.sprocketsports.com`; after
the user signs in, open `https://<club>.sprocketsports.com/dashboard` once so
the club site picks up the session, then load the team pages.

Sprocket's data endpoints (`/api/private/...`) need a bearer token the web app
holds and return 401 to a plain request. Read the rendered pages instead.

## Pages

- **Schedule** (`.../schedule`): a month view with previous and next arrows.
  Each game shows the date, start and end time, arrival time, venue name,
  full address, field, game type (Home or Away), uniform, opponent's full
  name, and, once played, the result as `W (3-1)`, `L (2-3)`, or `T (1-1)`.
  The score is the user's team first.
- **Results** (`.../results`): the season record and every game's score,
  with venue. It has no scorers or other events.
- **Roster & Staff** (`.../roster`): staff cards (name and title) and a
  player table with name and jersey number. Positions and starters are not
  recorded.

## Scorekeeper screenshots

Parents often send screenshots of the Sprocket app's Scorekeeper tab during
a game. Each one shows:

- the phone's status-bar time (minutes only)
- a CLOCK with seconds and a PERIOD (`1st Half`, `2nd Half`). The clock is
  marked "Clock is unofficial": the scorekeeper starts, stops, and changes
  period by hand, so it usually starts a few seconds after the real kickoff.
  In the second half it continues from the period length (`30:00` for
  2×30), so `35:16` in the 2nd half is 5:16 into the half. A clock paused
  with `START` showing just after the period changed marks the halftime
  whistle.
- the running score for both teams
- GAME HISTORY rows, newest first: the team, `Scored`, `Goal: <number>
  <name>` for the user's team, and the wall-clock time of the entry (minutes
  only). Names at the bottom of the screen are often cut off; resolve them
  by jersey number against the roster.

## Coach messages

Messages a coach posts to the team in the Sprocket app arrive by email from
`noreply@sprocketsports.com`, with the subject `<team name> You have a
message from <coach>` and the message text in the body. Search for that
sender and the team name around the game date.

## Using it in the report

- Match Details: date, kickoff time (the start time; arrival time is
  earlier), venue with field and address, home or away.
- The team's name is the program name at the top of the page.
- The result is the official score. When the video platform's tags disagree
  with it, follow Sprocket and tell the user.
- Coaching staff are the people on the staff cards, whatever their title (a
  director who coaches the team is the coach).
- Sprocket has no opponent roster.
