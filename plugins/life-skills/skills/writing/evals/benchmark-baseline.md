# Skill Benchmark: writing

**Model**: claude-sonnet-5 (executor), claude-opus-5-5 (analyzer)
**Date**: 2026-09-28
**Revision**: caf80c7 (PR dcwalker/ai-skills#76)
**Evals**: 1-30 (1 run each, with_skill only), graded strictly

## Summary

| Metric | With Skill |
|--------|------------|
| Expectation Pass Rate | 120/160 (75.0%) |
| Evals Fully Passed | 9/30 |
| Time | 139.0s ± 74.1s |
| Output Tokens | 11867 ± 6427 |
| Errors | 0 |
| Skill invoked | 30/30 trials |

Measured after adding the per-audience corpus and the vocabulary profile
(`scripts/vocabulary.py`), issue dcwalker/ai-skills#75.

## This baseline uses a stricter grading standard

The previous baseline (2026-08-25, 139/142, 97.9%) was graded more leniently.
Every run here was graded strictly and literally: any reason, time, cause,
promise, or conclusion the user did not state counts as invented, a menu of
tones does not count as asking the user to describe the register, and a note
that appears only in a cache file does not count as shown to the user.

Under that standard `main` (f331700) scored **75.1% (223/297)** across three
runs of the 19 evals that first looked regressed (2, 3, 5-8, 11, 12, 14-21,
24-26), with single runs ranging from 72.7% to 78.8%. The branch before its
QA fixes (a21316f) scored 75.4% on the same evals. Compare later results with
those numbers, graded the same way, and with at least three runs per eval:
one run moves by about ten points on its own.

## Per-eval results

| Eval | Scenario | Pass Rate | Time (s) | Tokens |
|------|----------|-----------|----------|--------|
| 1 | Peer email, rung-1 corpus | 4/6 | 137.6 | 13645 |
| 2 | New external recipient, rung-2 substitution | 3/5 | 187.9 | 18341 |
| 3 | No corpus anywhere | 4/5 | 27.0 | 2315 |
| 4 | Audience missing from the request | 4/4 | 16.5 | 1264 |
| 5 | Two artifacts, two audiences, one run | 5/5 | 276.5 | 26600 |
| 6 | Rewrite an assistant-sounding draft | 1/4 | 245.0 | 19592 |
| 7 | Explicit skip-the-research override | 3/4 | 16.7 | 1179 |
| 8 | Journal entry, audience is self | 2/4 | 133.3 | 11017 |
| 9 | Voice held across two revisions | 5/5 | 125.7 | 10825 |
| 10 | Cache belonging to different accounts | 4/4 | 239.6 | 20173 |
| 11 | Own cache reused and confirmed | 2/4 | 55.1 | 5063 |
| 12 | Blog post from posts on disk | 3/5 | 298.4 | 25007 |
| 13 | Jira comment, display-name collision | 5/5 | 141.8 | 12808 |
| 14 | Slack corpus from an on-disk export | 2/6 | 200.8 | 19579 |
| 15 | General-profile fallback, personal audience | 3/6 | 64.9 | 5166 |
| 16 | Slack corpus through the connector | 6/6 | 137.1 | 13450 |
| 17 | Two-sample corpus, confidence calibration | 4/5 | 162.1 | 11145 |
| 18 | Register mismatch, banter corpus, serious news | 3/5 | 101.9 | 8673 |
| 19 | Revision pushing against the observed voice | 4/5 | 213.5 | 14563 |
| 20 | Stale cached card, relationship drift | 5/6 | 173.7 | 16335 |
| 21 | Slack channel, retired account identifier | 4/6 | 137.5 | 12258 |
| 22 | Doc section, multi-author document | 5/6 | 72.1 | 6590 |
| 23 | Two horizons disagree, card extended | 5/6 | 151.3 | 14175 |
| 24 | Empty recent window, confidence capped | 4/6 | 114.5 | 10536 |
| 25 | Channel-scoped card, different channel | 6/6 | 117.0 | 11355 |
| 26 | Vocabulary slots and evidence thresholds | 6/6 | 106.3 | 10524 |
| 27 | Ledger appended, not rewritten | 6/7 | 193.6 | 7517 |
| 28 | Corpus labels, another writer's words quoted | 6/6 | 190.2 | 13424 |
| 29 | Dictated never-used word kept | 5/7 | 82.8 | 8092 |
| 30 | Pasted assistant draft, AI vocabulary not kept | 1/5 | 49.4 | 4792 |

## Findings

**The corpus kept other people's words out in every trial.** Across all 30
trials here, and every earlier branch trial, no segment written by someone
else was labeled as the user's, no corpus text leaked into a draft, and
nothing was sent, posted, or drafted in Gmail, Slack, or Jira. Eval 28 (quoted
corporate vocabulary from another writer) passed fully.

**Invented detail is the most common failure, and `main` shares it.** Evals 2,
7, 8, 12, 14, 15, 18, 20, 21, 22, 24, and 29 add a reason, promise, time, or
conclusion the user did not give, most often a line telling the recipient the
user is unavailable, taken from the prompt's instruction to the assistant.
These fail at similar rates on `main`.

**Eval 30 scored 1/5 on this revision.** Asked to make a pasted assistant draft
sound like the user, the model treated the draft as dictation and kept
"leverage", "robust", and "streamlines". 57f092a separates dictation from
source text in Step 1 and warns when the exempt file holds several never-used
words; three runs of eval 30 on that commit dropped the pasted vocabulary in
3 of 3.

## Cost

Trials take about 40% longer and use about 42% more output tokens than on
`main` (135s vs 96s mean on the 19-eval comparison), from saving the corpus
and running the check. Accepted as the tradeoff for the vocabulary profile.

## Keep when trimming SKILL.md

**Compressing the `$HOME` location rule is a known regression.** In the
2026-08-25 split, dropping four words -- "the one just printed" -- made eval 8
write its cache to the developer's real home directory instead of the trial's
(escape rate 0 in 54 trials before, 1 in 8 after). The words are back, with an
explicit "if you are about to type `/Users/`, stop". That paragraph is the only
thing standing between the skill and writing private observations, and now
raw correspondence, into the wrong home.

## Caveats

**Commits after caf80c7 were not re-run as a full suite:** 57f092a
(dictation vs pasted draft), 087de6f and 7949743 (SonarCloud fixes, including
limiting script paths to `$HOME` and `$TMPDIR`), aa83ed0 (dedupe key), 8a9f373
(Windows venv path), and 0dd7edd (docs). The path limit means a draft file in
a scratchpad under `/tmp` is refused and the model must retry with `mktemp`.

**wordfreq was available** through `WRITING_STYLE_VENV`, so keyness and the
rarity check ran. Under `AI_SKILLS_EVAL` without it, those checks are skipped.

**Trial workspaces were outside the repo** (`TRIALS_DIR`), so the repo's
AGENTS.md did not apply to trials.

**Eval 22's trigger is intermittent** (a request naming a file path rather
than a recipient); it fired here.
