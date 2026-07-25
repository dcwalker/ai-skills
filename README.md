# ai-skills

Personal Claude Code plugins and skills, distributed as a plugin marketplace.

## Plugins

- **life-skills** — Personal life-organization skills: `conduct-interview`, `organize-meeting-notes`, `triage`.
- **software-development** — Software development workflow skills: `analyze-logs`, `commit`, `create-branch`, `create-github-issue`, `fix-pr-checks`, `implement-feature`, `land-pr`, `pr`, `resolve-pr-comments`, `resolve-sonarqube-issues`, `review-code`, `review-readme`, `tidy-workspace`, `update-dependabot-bulk`.

## Installation

Add this repo as a plugin marketplace in Claude Code:

```
/plugin marketplace add dcwalker/ai-skills
```

Then install a plugin from it:

```
/plugin install life-skills@dcwalker-skills
/plugin install software-development@dcwalker-skills
```

Run `/plugin` to browse installed and available plugins, or to update/remove one later.
