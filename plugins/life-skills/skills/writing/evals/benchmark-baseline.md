# Skill Benchmark: writing

**Model**: claude-sonnet-5 (executor), claude-opus-5-5 (analyzer)
**Date**: 2026-10-08
**Revision**: PR dcwalker/ai-skills#97 (no change to the writing skill)
**Evals**: 1-30 (1 run each, with_skill only), graded strictly

## Summary

| Metric | With Skill |
|--------|------------|
| Expectation Pass Rate | 133/160 (83.1%) |
| Evals Fully Passed | 12/30 |
| Time | 146.3s ± 77.9s |
| Output Tokens | 9563 ± 4964 |
| Errors | 0 |
| Skill invoked | 30/30 trials |

Re-measured after the eval harness stopped leaking the developer's account
identity into trials (issue dcwalker/ai-skills#96). The writing skill itself
did not change. The previous baseline, 120/160 (75.0%) on 2026-09-28, may have
been recorded with the leak; its per-eval scores are shown alongside.

## The identity leak this baseline removes

Trials launched from a Claude Code session inherited `CLAUDE_CODE_USER_EMAIL`,
`CLAUDE_CODE_ACCOUNT_UUID`, and `CLAUDE_CODE_ORGANIZATION_UUID`. With them set,
the trial's model was told the developer's email, and Claude Code re-added
`oauthAccount` to the trial's sanitized `.claude.json`. Writing trials then
signed drafts with the developer's name and rejected a fixture persona's cached
profile as another account's (evals 15, 27, and 29 in a run before the fix).
`evals/lib/isolation-env.sh` now unsets all three. Earlier baselines may carry
the leak, which would explain part of why this one is higher with no skill
change; single-run variance and the missing wordfreq checks (see Caveats)
account for the rest.

## Grading standard

Every run was graded strictly and literally, as in the 2026-09-28 baseline: any
reason, time, cause, promise, or conclusion the user did not state counts as
invented, a menu of tones does not count as asking the user to describe the
register, and a note that appears only in a cache file does not count as shown
to the user. One run moves by about ten points on its own, so compare later
results with at least three runs per eval.

## Per-eval results

| Eval | Scenario | Pass Rate | 2026-09-28 | Time (s) | Output tokens |
|------|----------|-----------|------------|----------|---------------|
| 1 | Peer email, rung-1 corpus | 6/6 | 4/6 | 167.3 | 9573 |
| 2 | New external recipient, rung-2 substitution | 4/5 | 3/5 | 195.1 | 13312 |
| 3 | No corpus anywhere | 4/5 | 4/5 | 47.9 | 2929 |
| 4 | Audience missing from the request | 4/4 | 4/4 | 6.8 | 318 |
| 5 | Two artifacts, two audiences, one run | 5/5 | 5/5 | 235.4 | 20331 |
| 6 | Rewrite an assistant-sounding draft | 2/4 | 1/4 | 241.3 | 13955 |
| 7 | Explicit skip-the-research override | 3/4 | 3/4 | 15.0 | 887 |
| 8 | Journal entry, audience is self | 3/4 | 2/4 | 228.7 | 16395 |
| 9 | Voice held across two revisions | 4/5 | 5/5 | 99.2 | 6315 |
| 10 | Cache belonging to different accounts | 4/4 | 4/4 | 173.1 | 12406 |
| 11 | Own cache reused and confirmed | 4/4 | 2/4 | 59.4 | 4522 |
| 12 | Blog post from posts on disk | 3/5 | 3/5 | 230.4 | 18458 |
| 13 | Jira comment, display-name collision | 5/5 | 5/5 | 141.8 | 11926 |
| 14 | Slack corpus from an on-disk export | 2/6 | 2/6 | 178.3 | 12731 |
| 15 | General-profile fallback, personal audience | 4/6 | 3/6 | 65.4 | 3594 |
| 16 | Slack corpus through the connector | 5/6 | 6/6 | 115.7 | 8376 |
| 17 | Two-sample corpus, confidence calibration | 3/5 | 4/5 | 244.9 | 15770 |
| 18 | Register mismatch, banter corpus, serious news | 3/5 | 3/5 | 86.8 | 6884 |
| 19 | Revision pushing against the observed voice | 4/5 | 4/5 | 240.9 | 11602 |
| 20 | Stale cached card, relationship drift | 5/6 | 5/6 | 118.0 | 10014 |
| 21 | Slack channel, retired account identifier | 5/6 | 4/6 | 156.5 | 11067 |
| 22 | Doc section, multi-author document | 6/6 | 5/6 | 253.8 | 7822 |
| 23 | Two horizons disagree, card extended | 6/6 | 5/6 | 123.5 | 10958 |
| 24 | Empty recent window, confidence capped | 6/6 | 4/6 | 123.2 | 6930 |
| 25 | Channel-scoped card, different channel | 6/6 | 6/6 | 109.3 | 9120 |
| 26 | Vocabulary slots and evidence thresholds | 6/6 | 6/6 | 147.3 | 10087 |
| 27 | Ledger appended, not rewritten | 7/7 | 6/7 | 148.4 | 7773 |
| 28 | Corpus labels, another writer's words quoted | 4/6 | 6/6 | 307.8 | 13866 |
| 29 | Dictated never-used word kept | 6/7 | 5/7 | 61.9 | 4576 |
| 30 | Pasted assistant draft, AI vocabulary not kept | 4/5 | 1/5 | 64.9 | 4401 |

## Findings

**Invented detail is still the most common failure.** Evals 2, 6, 8, 12, 17,
18, 19, and 20 add a reason, promise, time, or conclusion the user did not
give.

**Eval 28 dropped (4/6 from 6/6)** because its one `vocabulary.py check` was
run in the background on an earlier draft, printed nothing, and was killed; the
draft shown was never checked by the script. Eval 26 ran the same check in the
same environment and it finished at once, so this looks like a hang in that
trial rather than a skill change.

**Eval 14 still never reads the on-disk Slack export** and builds its card from
adjacent email instead.

## Keep when trimming SKILL.md

**Compressing the `$HOME` location rule is a known regression.** In the
2026-08-25 split, dropping four words -- "the one just printed" -- made eval 8
write its cache to the developer's real home directory instead of the trial's
(escape rate 0 in 54 trials before, 1 in 8 after). The words are back, with an
explicit "if you are about to type `/Users/`, stop". That paragraph is the only
thing standing between the skill and writing private observations, and now
raw correspondence, into the wrong home.

## Caveats

**wordfreq was not available** (no `WRITING_STYLE_VENV`), so keyness and the
rarity check were skipped. The 2026-09-28 baseline ran with them, so the two
runs differ in that check as well as in the identity leak.

**Trial workspaces were outside the repo** (`TRIALS_DIR`), so the repo's
AGENTS.md did not apply to trials.

**Trials can still read outside their run directory.** Eval 5 ran `find` over
the developer's real home; writes there are refused, reads are not.
