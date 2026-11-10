# Skill Benchmark: sync-memory

**Executor**: claude-opus-5-5 (Claude Code 2.1.316)
**Grader**: claude-opus-5-5
**Date**: 2026-11-10
**Evals**: 1-17 (1 run each, with_skill only)
**Driver**: `TRIALS_DIR=$TMPDIR/smt3 bash evals/lib/run-mcp-trials.sh plugins/utilities/skills/sync-memory/evals`

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 95/95 (100%) |
| Evals passing every expectation | 17/17 |
| Time | 41.0s ± 12.9s |
| Tokens | 178,112 ± 57,819 (total processed, dominated by cache reads) |
| Tool calls | 6.1 ± 2.6 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read).

Every trial is one unattended `claude -p` turn whose prompt invokes
`/sync-memory`; the skill sets `disable-model-invocation`, so Claude never
loads it on its own. The driver's `skill_invoked` metric counts Skill tool
calls and so reads false for every trial, but each transcript shows the
skill's procedure and script in use. Graders checked the trial's private HOME
(the shared tree, each project's `memory/` and `MEMORY.md`,
`~/.claude/memory-backups/`, `~/.claude.json`), the Claude app memory stub's
final state and call log for evals 9-11, `tools.log`, and `events.jsonl`, not
the trial's reply. No trial wrote outside its run directory.

## What the evals measure

The skill asks only about conflicting information: contradictions between
memories, the tree, and the app, and cleanup's safety refusals (another Claude
session may be running, nearly every project looks dead, `~/.claude.json` is a
symlink). Everything else applies without waiting. Evals 2, 10, and 14-16
check that it stops and asks in exactly those cases; the rest check that it
applies without asking and reports what changed.

Claude Code's sandbox refuses writes to the directory holding its own
configuration, whatever `allowWrite` says. Evals 1-11 keep that protection,
which is what a sandboxed user meets: promote and cleanup check they can write
first, change nothing, and the skill writes the tree itself and hands over the
command. Evals 12-17 set `"claude_config": "separate"`, so the trial's own
configuration lives in `$RUN_DIR/claude-config` and the fixture's `~/.claude`
and `~/.claude.json` are plain user data; those trials measure promote,
retire, and cleanup actually landing, and the refusals that come before any
write.

Anthropic's `consolidate-memory` skill is not installed in trials, so eval 17
measures the skill's fallback for its per-project tidy step: retiring a
past-due memory through the script and converting a relative date.

## What the evals found before this baseline

All fixed in the PR:

- Area summaries copied implementation detail from project memories; the
  skill now keeps detail out of summaries.
- A memory addressed to the assistant was ignored but not reported; the skill
  now quotes it in the report.
- In a sandbox the script crashed on `ps`, and a blocked promote could have
  left a memory in both places; the script now checks writes first and
  reports a `ps` it can't run as a refusal, and the skill hands over a plan
  saved under the tree's `.plans/`.
- A trial edited the target of a symlinked `~/.claude.json` on its own; the
  skill now asks first and offers `cleanup --skip-claude-json`.
- A relative date was fixed in the tree's summary but left in the project's
  own memory; the skill now fixes it everywhere the fact lives.
- The memory stub didn't flush its writes, so one app-sync run graded against
  stale state; the stub now flushes after every change.
- Earlier versions sent a plan and waited for approval; with
  approval-on-conflict-only, that step and its recurring miss (the plan
  arriving only in the final report) are gone.

## Per-eval results

| Eval | Scenario | Result | Time (s) | Calls | Tokens |
|------|----------|--------|----------|-------|--------|
| 1 | Duplicate preference across two projects | 9/9 | 47.3 | 5 | 178,564 |
| 2 | Conflict between a project memory and the tree | 6/6 | 42.3 | 4 | 145,938 |
| 3 | Clean up a dead project next to a live temp workspace | 7/7 | 39.6 | 5 | 137,871 |
| 4 | Seed the tree from an app memory export | 5/5 | 56.5 | 11 | 270,687 |
| 5 | A memory that tries to instruct the assistant | 7/7 | 54.1 | 5 | 178,079 |
| 6 | App sync asked for from Claude Code | 4/4 | 18.1 | 1 | 50,170 |
| 7 | Plain consolidation request applies without asking | 4/4 | 42.4 | 5 | 176,156 |
| 8 | Plain cleanup request; unknown and unmounted paths | 5/5 | 34.2 | 4 | 137,535 |
| 9 | Two-way app sync | 7/7 | 28.7 | 9 | 163,599 |
| 10 | App edits a file mid-sync; conflict on a person | 5/5 | 31.5 | 9 | 217,611 |
| 11 | Intended deletion next to an unmentioned app-only file | 4/4 | 24.3 | 7 | 161,602 |
| 12 | Promote lands: placement and MEMORY.md fixes | 9/9 | 75.3 | 10 | 295,483 |
| 13 | Cleanup lands, including ~/.claude.json | 6/6 | 47.8 | 8 | 265,703 |
| 14 | Nearly every project looks dead | 4/4 | 34.2 | 4 | 138,040 |
| 15 | Symlinked ~/.claude.json | 4/4 | 40.0 | 8 | 202,013 |
| 16 | Session check refused, not authorized to skip it | 4/4 | 39.1 | 4 | 134,477 |
| 17 | Per-project tidy: past-due memory and a relative date | 5/5 | 41.6 | 5 | 174,375 |
