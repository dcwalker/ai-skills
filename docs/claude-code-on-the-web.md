# Claude Code on the web

The README's [Installation](../README.md#installation) steps cover a local install. A cloud session gets neither of them:
it clones the repository, but marketplace registrations and installed plugins
live in `~/.claude` on the machine where `/plugin` ran, so they do not travel.
`/plugin` is also unavailable in cloud sessions, leaving no in-session way to
add them. A fresh cloud session therefore reports `No plugins installed`, and
`/software-development:land-pr` comes back as an unknown command.

Install them from the cloud environment's **Setup script** instead, which runs
before Claude Code launches. Open the environment dialog at
[claude.ai/code](https://claude.ai/code) and set:

```bash
#!/bin/bash
claude plugin marketplace add dcwalker/ai-skills || true
claude plugin install life-skills@dcwalker-skills --scope user || true
claude plugin install software-development@dcwalker-skills --scope user || true
claude plugin install utilities@dcwalker-skills --scope user || true
```

The `|| true` matters, and it cuts both ways. A setup script that exits
non-zero fails the session outright, so without it a transient network error
during an install would cost you the whole session rather than one plugin. But
exiting zero is also what tells Claude Code the script succeeded, and it
snapshots the filesystem at that point and starts every later session from that
snapshot. A swallowed install error is therefore cached rather than retried:
the environment comes back missing that plugin every time, because the script
runs once per environment rather than once per session.

To check whether that happened, run `claude plugin list` in a session. To recover, edit the
setup script: any change to it, or to the environment's allowed network hosts,
rebuilds the snapshot and re-runs the install. Left alone, the cache rebuilds
by itself after roughly seven days.

Two consequences worth knowing:

- The setup script belongs to the environment, not to this repository, so it
  applies to every repo you open in that environment and is lost if the
  environment is recreated. That is why it is written down here.
- Installing at `--scope user` deliberately leaves local sessions alone. The
  alternative, committing `extraKnownMarketplaces`/`enabledPlugins` to
  `.claude/settings.json`, would apply everywhere but project settings outrank
  user settings — so in this repository a committed marketplace would shadow a
  local checkout-based install and load the skills as published on the default
  branch. Editing a skill on a branch and then invoking it would run the
  pre-edit version, which is precisely the wrong behavior in the repository
  where these skills are authored.
