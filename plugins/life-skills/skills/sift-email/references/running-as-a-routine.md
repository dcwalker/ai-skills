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
  allows.
