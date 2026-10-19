# TeamSnap

TeamSnap hosts team schedules, rosters, and messages at
`https://go.teamsnap.com`. The pages render as plain HTML for a signed-in
user, so read them directly in the user's browser.

## Pages

- **Dashboard** (`/team/dashboard`): the user's teams and upcoming events.
- **Full schedule** (`/team/schedule`): a month calendar. Each game shows the
  time, arrival time, opponent (`vs.` for home, `at` for away), location, and
  once played the result as `W 4-0`, `L 1-2`, or `T 1-1`, with the user's
  team first.
- **Game page** (`/<team id>/schedule/view_game/<game id>`): date and time,
  arrival time, location name and details, a map link, opponent, home or
  away, uniform, notes (which may carry a league game ID or other details),
  each player's availability with jersey number, and the result.
  Availability is a response, not attendance: a player marked unavailable
  is marked Absent in the report, but available does not prove the player
  played.
- **Roster** (`/<team id>/roster`): players with jersey number and position
  when recorded (`# / Position`), and staff with roles such as Coach and
  Team Manager.
- **Statistics** (`/<team id>/statistics`): per-game stats only if the team
  manager configured the module; often empty.
- **Media** (`/<team id>/files`): photos, files, and a Videos view where the
  team may post recording links.
- **Messages**: team emails also arrive in the user's mail from
  `donotreply@email.teamsnap.com` with the team name in brackets in the
  subject; search there for coach notes and recording links.

## Using it in the report

- Match Details: date, kickoff time (not arrival time), location and
  address, home or away.
- The result on the game page is the official score.
- Coaching staff are the roster's staff entries with a coaching role; list a
  team manager on their own line only if the user wants staff beyond the
  coach.
- Positions from the roster map to GK, DEF, MID, and FWD.
- TeamSnap has no opponent roster.
