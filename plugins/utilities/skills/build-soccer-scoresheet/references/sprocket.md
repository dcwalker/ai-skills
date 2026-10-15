# Sprocket

Sprocket Sports hosts club websites with team schedules, results, and
rosters. A club's site is `https://<club>.sprocketsports.com`, and a team's
pages live under `/team/<team id>/program/<program id>/`. Everything useful
needs the user to be signed in; signed out, the pages redirect to the club's
public homepage.

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

## Using it in the report

- Match Details: date, kickoff time (the start time; arrival time is
  earlier), venue with field and address, home or away.
- The team's name is the program name at the top of the page.
- The result is the official score. When the video platform's tags disagree
  with it, follow Sprocket and tell the user.
- Coaching staff are the people on the staff cards, whatever their title (a
  director who coaches the team is the coach).
- Sprocket has no opponent roster.
