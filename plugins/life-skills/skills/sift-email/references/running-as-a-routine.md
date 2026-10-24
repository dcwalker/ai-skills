# Running sift-email as a routine

Sift is meant to run as a scheduled cloud routine. The routine needs:

- **Connectors:** Gmail, Claude Docs, and the Google Contacts connector. A
  routine includes the account's connectors by default; keep these three.
- **This skill's repository** attached to the routine, so each run has a
  checkout of it.
- **A prompt that reads the skill from the checkout,** with the docs' links
  once they exist, for example: "Sift my inbox. Read
  plugins/life-skills/skills/sift-email/SKILL.md in this repository, and the
  files in its references/ folder, and follow them as the sift-email skill's
  instructions for this run. Rubric: <link> Log: <link>"
- **A schedule** of an hour or longer between runs, the shortest a routine
  allows. Most runs find nothing new and stop early, so a few runs a day cost
  far less than hourly ones.

A routine run can have a push notification tool even when the routine's
allowed tools don't list it, and may use it to report a run. Sift sends one
only for mail the rubric's Notify section describes, so an empty Notify keeps
every run silent apart from the log.

## Why the checkout, not the plugin

Two things get in the way of invoking the installed skill from a routine:

- **The skill runs only when called directly.** Its frontmatter sets
  `disable-model-invocation: true`, so Claude never starts a bulk-labeling run
  on its own. That setting also stops the skill from running when a scheduled
  task fires with it as the prompt.
- **Plugins reach a routine late.** A cloud session gets plugins only from the
  environment's setup script, and that script's result is cached, so a new
  release of this skill reaches the routine only after the cache rebuilds
  (edit the setup script, or wait about seven days).

Reading SKILL.md from the checkout avoids both: every run follows the
skill as it is on the repository's default branch. Anything merged there
reaches the routine on its next run.

## Setting it up

1. Create the routine with its schedule turned off, and leave the doc links
   out of the prompt. Say instead that this is the first run, so sift creates
   the rubric and log.
2. Run it once by hand. Its summary reports the two doc links.
3. Add the links to the prompt, then turn on the schedule.
4. Set the rubric's Timezone line, so log times read in local time.

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
