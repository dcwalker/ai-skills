# Veo

Veo records the match on a sideline camera and tags events with AI. It has no
documented public API. The endpoints below are the ones Veo's own web app
calls, observed in October 2026; they can change without notice. Try them
first, and fall back to reading the match page in the user's signed-in
browser when they fail.

A match URL looks like `https://app.veo.co/matches/<slug>/`, where the slug is
the date plus a title, for example
`20260919-home-team-vs-away-team-1a2b3c4d`.

## What Veo provides

| Data | Signed out | Signed in |
|------|------------|-----------|
| Match title, opponent, home or away, age group | Yes | Yes |
| Recording start and end (wall clock, with UTC offset) | Yes | Yes |
| Aggregated final score | Yes | Yes |
| Period boundaries (seconds into the recording) | Yes | Yes |
| AI clips for goals and shots (no team) | Yes | Yes |
| Full event list with team and running score | No | Yes, in the Events panel |
| Player names on events | Only when someone tagged them by hand | Same |
| Cards and substitutions | No | No |

Veo does not record who scored, cards, or substitutions unless a team member
adds them by hand. Those still come from the notes and screenshots.

## API (try first)

Fetch these from a page on `app.veo.co` (for example with the browser's
`fetch` in the match page), so the user's session applies when present.

- `GET /api/app/matches/<slug>/`: `start` and `end` are the recording's
  wall-clock start and end with UTC offset; `duration` is in seconds;
  `opponent_team_name`, `own_team_home_or_away`; `info.stats.score_aggregated`
  holds `{own, opponent}`. The aggregated score comes from AI tags and can
  credit the opponent's goals to the user's team (one 1-3 loss showed as
  3-1); the team app's result wins over it. `own_team_home_or_away` is set
  with the upload and can be wrong too; take home or away from the team app
  or its calendar event.
- `GET /api/app/matches/<slug>/periods/`: a list of periods, each with
  `timeframe: [start, end]` in seconds from the recording start, `duration`,
  and `own_side`. `is_confirmed: false` means AI-detected; treat the
  boundaries as good to a few seconds. Kickoff of a period in wall-clock time
  is the match `start` plus `timeframe[0]`.
- `GET /api/app/matches/<slug>/highlights/?include_ai=true`: clips, each with
  `start` (seconds into the recording), `duration`, `type` (`goal`,
  `shot_on_goal`, and others), `team_association` (often null for AI clips),
  and `involved_players` (often empty). A clip starts several seconds before
  its event; in one observed goal the event was about 9 seconds after the
  clip's `start`.
- The full event list (`/api/mes/v2/<match id>/match-events`) and the lineup
  and roster endpoints need an authorization token the web app holds, and
  return 401 or 403 to a plain request. Do not try to extract the token; use
  the Events panel instead.

## Events panel (fallback, and the only source of event links)

With the user signed in, open the match page and select the Events panel
(the list icon in the right-hand toolbar). Each card shows a minute, the
team's short name, an `AI` badge when the tag is automatic, the event type
(Kickoff, Goal, Shot, Corner, Free kick, Foul, Throw-in, Goal kick), and for
goals the running score. Section headers mark `1ST PERIOD`, `2ND PERIOD`, and
so on. The list is virtualized, so scroll it to read every card. The team on
an AI card can be wrong (a penalty the opponent scored was tagged to the
user's team); follow the team app and the notes for who scored. The
player's timeline below the video also has one button per event, labeled
with the event type (`Goal`, `Kickoff`) and all rendered at once; clicking
one seeks to its event and sets the `?event=` link, as a card does.

The minute on a card is continuous and has no stoppage notation (in 2×30, the
second half starts at `31'` and stoppage shows as `61'`, `62'`). It can also
carry first-half stoppage into the second half: a goal 5:01 into the second
half of a 2×30 game showed as `37'` where the report needs `36'`. Recompute
every minute from the period kickoffs.

**Period kickoffs.** The `Kickoff` cards are better kickoff anchors than the
`periods` timeframes, which are AI-detected and were a few seconds late in
one match. Click the first Kickoff card under each period header and read
the video's `currentTime`; later Kickoff cards in a period are restarts after
goals. Pause the video before clicking and read `currentTime` on the video's
`seeked` event: a playing video moves on, and a reading taken a few seconds
after the click is a few seconds late.

**Goals.** The `Goals` quick filter lists only goals. Clicking each goal
card gives its exact time (`currentTime`), its team, the running score, and
its `?event=` link in one pass.

Clicking a card seeks the video to that event and changes the page URL to
`https://app.veo.co/matches/<slug>/?event=<event id>`. The video's
`currentTime` after the click is the event's offset in seconds from the
recording start. That `?event=` URL is the event's video link for the report;
it opens at the event only for viewers signed in to Veo with access to the
match (signed out, it shows a login prompt and stays at the start).

## Looking at a moment

To check who is involved in an event (Step 5 of the skill), open the match
page signed in, set the video element's `currentTime` to the event's offset
in seconds (or click its card in the Events panel), pause, and take
screenshots, zooming on the players. The default view follows the ball.
The match's `permissions` list the other video modes the viewer can use
(`read_match__video_mode_panorama`, `..._interactive`); a panorama shows the
whole pitch, including the touchline where substitutions happen. The `/videos/` endpoint
also lists MP4 URLs, but downloading one needs the user's permission.

## Recording link

Use the match URL. The report line is
`[Veo | <match title>](https://app.veo.co/matches/<slug>/)`, with the title as
Veo shows it.
