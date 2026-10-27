# Running sift-email as a routine

Sift is meant to run as a scheduled cloud routine. The routine needs:

- **Connectors:** Gmail and the Google Contacts connector. A routine includes
  the account's connectors by default; keep these two.
- **Two repositories attached:** this skill's repository, so each run has a
  checkout of the skill, and the private repository that holds
  `sift-email/rubric.md` and the state files. A routine's session can
  reach only the repositories attached to it: it clones each one beside the
  others, and it can't search GitHub, so sift finds the rubric in those
  checkouts. Sift commits and pushes to that repository's default branch.
- **A prompt that reads the skill from the checkout,** for example: "Sift my
  inbox. Read plugins/life-skills/skills/sift-email/SKILL.md in this
  repository, and the files in its references/ folder, and follow them as
  the sift-email skill's instructions for this run." It needs no links or
  repository names: sift finds its files by their content.
- **A schedule** of an hour or longer between runs, the shortest a routine
  allows. Most runs find nothing new and stop early without a commit, so
  a few runs a day cost far less than hourly ones.

A routine run can have a push notification tool even when the routine's
allowed tools don't list it, and may use it to report a run. Sift sends one
only for mail the rubric's Notify section describes, so a missing or empty
Notify keeps every run silent apart from its commit.

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

1. Create a private repository for sift's files, or pick one you already
   own. Sift checks that the repository is yours and private before it reads
   or writes anything there.
2. Run sift once by hand, in a conversation. When it can't find the rubric,
   it asks which of your private repositories and which folder should hold
   the files, creates them there, and pushes them.
3. Set the rubric's Timezone line, so dates read in local time.
4. Create the routine with both repositories attached and the prompt above,
   then turn on the schedule.

## More than one Gmail account

Each Gmail account needs its own run: a routine whose Gmail connector is
signed in to that account, or a run by hand in a session connected to it.
Attach the same two repositories and use the same prompt. Every account
shares the rubric, and sift keeps a separate `state-<account>.md` for each,
naming the account it finds from Gmail, so nothing in the prompt has to say
which account it is.

Give each routine a different minute of the hour, such as `0` and `30`, so
two runs rarely save at once. When they do, the second push is rejected and
sift rebases onto the first before pushing again.

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
