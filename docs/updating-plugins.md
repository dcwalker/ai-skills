# Updating an installed plugin

Installing a plugin copies it at a specific commit, into a directory named after
that commit — one such directory per plugin, `life-skills` shown here:

```text
~/.claude/plugins/cache/dcwalker-skills/life-skills/
├── c2eeda74d2a9/skills/   conduct-interview, organize-meeting-notes, triage
└── ea42d071a0d5/skills/   the same three, plus writing
```

That copy is what loads, and it stays pinned to its commit. Refreshing the
marketplace does not move it: the marketplace is a separate clone holding the
catalog, so a refresh gives you a current *listing* of what is available while
the plugin keeps loading the skills it was installed with. A skill added after
you installed will not appear, and nothing reports an error, because from the
plugin's point of view nothing is wrong.

Updating is therefore two stages, and the second is the one that matters:

```bash
claude plugin marketplace update dcwalker-skills
claude plugin update life-skills@dcwalker-skills
claude plugin update software-development@dcwalker-skills
claude plugin update utilities@dcwalker-skills
```

The marketplace update is shared; each installed plugin then needs its own
update. Updating one does not touch the others, so a skill added to
`software-development` stays missing until that second line runs.

The equivalents live under `/plugin` in the app: update the marketplace, then
update each plugin (uninstalling and reinstalling has the same effect). Either
way, **restart afterwards** — the update prints `Restart to apply changes`, and
skills are enumerated when a session starts, so a session already running keeps
the old set.

To check that an update actually landed, ask which commit each plugin is pinned
to:

```bash
claude plugin list
```

Matching versions across all plugins, at the commit you expect, means the
update worked and only a restart is missing. A plugin still showing the old
commit was not updated — most likely its `plugin update` line was skipped, or
the marketplace update failed first.

Do not judge this by the cache directory. Updating one plugin can materialize a
new commit directory for the *other* one without repointing it, so
`ls ~/.claude/plugins/cache/dcwalker-skills/*/*/skills/` will happily show a
directory containing the new skill for a plugin that is still loading the old
copy. What decides is the `installPath` recorded per plugin in
`~/.claude/plugins/installed_plugins.json`, which is what `claude plugin list`
reports.
