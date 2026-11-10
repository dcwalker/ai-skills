# Skill Benchmark: sync-memory

**Executor**: claude-opus-5-5 (Claude Code 2.1.316)
**Grader**: claude-opus-5-5
**Date**: 2026-11-10
**Evals**: 1-16 (1 run each, with_skill only)
**Driver**: `TRIALS_DIR=$TMPDIR/cmt5 bash evals/lib/run-mcp-trials.sh plugins/utilities/skills/sync-memory/evals`

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 89/91 (97.8%) |
| Evals passing every expectation | 14/16 |
| Time | 36.2s ± 11.8s |
| Tokens | 171,374 ± 57,680 (total processed, dominated by cache reads) |
| Tool calls | 6.1 ± 2.6 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read).

Every trial is one unattended `claude -p` turn. Graders checked the trial's
private HOME (the shared tree, each project's `memory/` and `MEMORY.md`,
`~/.claude/memory-backups/`, `~/.claude.json`), the Claude app memory stub's
final state and call log for evals 9-11, `tools.log`, and the order of events
in `events.jsonl`, not the trial's reply. All 16 trials loaded the skill, and
none wrote outside its run directory.

## Two ways the evals reach ~/.claude

Claude Code's sandbox refuses writes to the directory holding its own
configuration, whatever `allowWrite` says. Evals 1-11 keep that protection,
which is what a sandboxed user meets: promote and cleanup check they can write
first, change nothing, and the skill writes the tree itself and hands over the
command. Evals 12-16 set `"claude_config": "separate"`, so the trial's own
configuration lives in `$RUN_DIR/claude-config` and the fixture's `~/.claude`
and `~/.claude.json` are plain user data; those trials measure promote and
cleanup actually landing, and the refusals that come before any write.

## Open finding

**The plan doesn't go out before the first change when applying is
pre-authorized** (eval 1 and eval 12, one expectation each). Asked to "show me
the plan, then apply it without waiting", both trials read the memories and
went straight to writing, and the plan first appeared in the final report.
SKILL.md says this in step 5 and again at the start of step 6, and the same
miss appeared in every earlier run, so wording alone has not moved it. When
the user has not authorized applying (eval 7), the skill stops at the plan as
it should.

## What the evals found before this baseline

All fixed in the PR:

- Area summaries copied implementation detail (a cache's settings) from
  project memories; SKILL.md now keeps detail out of summaries.
- A memory addressed to the assistant was ignored but not reported; the skill
  now quotes it in the plan and report.
- In a sandbox the script crashed on `ps`, and a blocked promote could have
  left a memory in both places; the script now checks writes first, reports a
  `ps` it can't run as a refusal, and the skill hands over a plan saved under
  the tree's `.plans/`.
- Eval 15 edited the target of a symlinked `~/.claude.json` on its own; the
  skill now asks first and offers `cleanup --skip-claude-json`.
- The memory stub didn't flush its writes, so the first app-sync run graded
  against stale state; the stub now flushes after every change.

## Per-eval results

| Eval | Scenario | Result | Time (s) | Calls | Tokens |
|------|----------|--------|----------|-------|--------|
| 1 | Duplicate preference across two projects, apply authorized | 8/9 | 39.6 | 5 | 162,075 |
| 2 | Conflict between a project memory and the tree | 6/6 | 36.0 | 4 | 131,755 |
| 3 | Clean up a dead project next to a live temp workspace | 7/7 | 37.7 | 7 | 184,737 |
| 4 | Seed the tree from an app memory export | 5/5 | 53.4 | 10 | 226,253 |
| 5 | A memory that tries to instruct the assistant | 7/7 | 51.1 | 6 | 196,956 |
| 6 | App sync asked for from Claude Code | 4/4 | 21.2 | 3 | 93,520 |
| 7 | Consolidate without authorization to apply | 4/4 | 21.6 | 3 | 99,329 |
| 8 | Cleanup without authorization; unknown and unmounted paths | 6/6 | 25.4 | 3 | 97,510 |
| 9 | Two-way app sync | 7/7 | 28.3 | 8 | 181,173 |
| 10 | App edits a file mid-sync; conflict on a person | 5/5 | 44.3 | 11 | 237,419 |
| 11 | Intended deletion next to an unmentioned app-only file | 4/4 | 23.6 | 8 | 203,968 |
| 12 | Promote lands: placement and MEMORY.md fixes | 8/9 | 62.5 | 10 | 306,575 |
| 13 | Cleanup lands, including ~/.claude.json | 6/6 | 44.0 | 7 | 220,626 |
| 14 | Nearly every project looks dead | 4/4 | 28.5 | 4 | 124,951 |
| 15 | Symlinked ~/.claude.json | 4/4 | 31.5 | 5 | 150,926 |
| 16 | Session check refused, not authorized to skip it | 4/4 | 30.3 | 4 | 124,214 |
