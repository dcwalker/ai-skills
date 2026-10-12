# Running sift-email as a routine

Sift is meant to run as a scheduled cloud routine. The routine needs:

- **Connectors:** Gmail, Claude Docs, and the Google Contacts connector. A
  routine includes the account's connectors by default; keep these three.
- **The docs' links in its prompt,** for example: "Run sift-email. Rubric:
  <link>. Log: <link>." Leave them out on the first run; the summary reports
  the links to add.
- **The plugin installed** by the cloud environment's setup script, since
  locally installed plugins do not reach cloud sessions. The setup script's
  result is cached, so a newly released version of this skill reaches the
  routine only after the cache rebuilds (edit the setup script, or wait about
  seven days).
- **A schedule** of an hour or longer between runs, the shortest a routine
  allows. Most runs find nothing new and stop early, so a few runs a day cost
  far less than hourly ones.

## Running at set times of day

A routine's schedule is a cron expression, so it can list specific hours. Cron
runs in UTC, not local time: convert each local hour by the timezone's UTC
offset. For example, to run at 6am, noon, 6pm, and midnight where local time
is UTC−5, add 5 hours to each:

| Local | UTC |
|---|---|
| 6:00 am | 11:00 |
| 12:00 pm | 17:00 |
| 6:00 pm | 23:00 |
| 12:00 am | 05:00 |

which is `0 5,11,17,23 * * *`: minute 0 of those four UTC hours, every day.

Cron does not follow daylight saving. When local clocks change, the same
expression runs an hour earlier or later in local time. To keep the local
hours year-round, update the expression when the clocks change, here to
`0 4,10,16,22 * * *` while local time is UTC−4.
