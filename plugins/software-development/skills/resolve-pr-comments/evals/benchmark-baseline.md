# Skill Benchmark: resolve-pr-comments

**Model**: claude-opus-5
**Date**: 2026-08-13T05:20:00Z
**Evals**: 1–13 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Eval pass rate | 13/13 (100%) |
| Expectation pass rate | 55/56 (98.2%) |
| Time | 86.2s ± 15.6s (n=13) |
| Tokens | 43,948 ± 1,400 (n=13) |
| Tool calls | 10.4 ± 2.2 (n=13) |

The one non-passing expectation is a defect in the eval, not in the skill. See
Findings.

## Per-eval results

| Eval | Scenario | Pass | Time (s) | Tokens | Tools |
|------|----------|------|----------|--------|-------|
| 1 | Valid defect: off-by-one loop bound | 5/5 | 109.6 | 47,791 | 13 |
| 2 | Question, not a defect: retry backoff rationale | 4/4 | 92.0 | 43,427 | 9 |
| 3 | Already fixed before the run | 4/4 | 58.9 | 41,956 | 7 |
| 4 | Scoped to bot comments only | 4/5 | 75.4 | 42,742 | 9 |
| 5 | Scoped to human comments only | 4/4 | 93.3 | 43,531 | 11 |
| 6 | Two comments: one valid, one invalid | 5/5 | 93.6 | 44,110 | 11 |
| 7 | No comments on the PR | 4/4 | 88.2 | 46,167 | 10 |
| 8 | Request that violates a project convention | 4/4 | 65.9 | 42,197 | 7 |
| 9 | Magic number → shared constant | 4/4 | 99.5 | 43,999 | 12 |
| 10 | Hardcoded credential | 4/4 | 83.9 | 43,485 | 12 |
| 11 | Two independent valid defects | 4/4 | 108.7 | 45,821 | 14 |
| 12 | Sole comment already resolved | 4/4 | 64.0 | 41,558 | 7 |
| 13 | Comment links in the report (added in #41) | 5/5 | 88.0 | 44,551 | 12 |

Grading read each trial's final state — commits since the fixture baseline,
content diffs, working-tree cleanliness, and the ordered `gh` stub call log —
rather than the executor's own account. That mattered at least once: eval 2's
executor reported issuing a reply and a resolve, and a partial read of its call
log appeared to show neither. The full 22-call log confirmed both writes, with
the reply text present verbatim.

## Findings

### 1. SKILL.md documents an interface the bundled script does not have

Six places in `SKILL.md` instruct the agent to run:

```
list-pr-comments.sh --reply <comment-id> "Addressed in [SHA]."
list-pr-comments.sh --resolve <comment-id>
```

`--reply` takes only the reply text; the comment id must arrive via
`-c/--comment-id`. The working form is
`list-pr-comments.sh -c 3003 --reply "..." --resolve`.

Every trial still passed because line 46 tells the agent to read `--help`
first, and each executor did, then self-corrected. That instruction is silently
load-bearing: it is compensating for six wrong examples, and an agent that
skipped it would fail on its first write. Not fixed in this iteration on
purpose — the runs were already in flight, and editing the skill mid-sweep
would have produced a baseline for a version that never existed as a whole.
Fixing it is a follow-up, and warrants a re-benchmark since removing the
`--help` detour may change timing and token counts.

### 2. Eval 4's fifth expectation is not gradeable

> The `list-pr-comments.sh` invocation(s) used to gather comments included the
> `--bots` filter.

Nothing observable records this. `GH_STUB_LOG` captures `gh` invocations, and
`list-pr-comments.sh` issues a single GraphQL query and filters client-side, so
no `--bots` flag ever reaches the log. It also grades *how* the skill worked
rather than what it produced, which cuts against this repo's outcome-focused
grading rule. The outcome it is proxying for — only the bot comment acted on —
is already covered by expectation 4, which passed on hard evidence (zero `gh`
calls referencing comment 3005 or its thread). Recommend rewriting or dropping
it; it is recorded as failing here so the baseline does not overstate coverage.

### 3. Cassette replay confuses every executor identically

The `gh` stub replays a fixed cassette, so a read after a successful write
still returns the pre-mutation state. All thirteen executors noticed, and all
thirteen correctly diagnosed it as replay rather than a failed write, verified
against the call log, and declined to edit fixtures to force agreement. No
action needed — the behavior is correct and the executors handled it — but it
costs a turn or two per trial and is worth a line in the fixture docs.

## Notes

- Expectation verdicts combine programmatic checks of the final state (commit
  counts, changed paths, per-comment reply and `resolveReviewThread` calls and
  their ordering) with judgment on the subjective ones (whether a reply answers
  the question asked, whether a decline is well reasoned).
- Eval 13 is new in #41 and passes: the report links PR #64 and both comments
  as distinct Markdown hyperlinks, with no fabricated URLs.
- Evals 4 and 5 are mirror images (bot-only, human-only) and both scoped
  correctly, including leaving the out-of-scope comment entirely untouched
  rather than replying to explain the deferral.
