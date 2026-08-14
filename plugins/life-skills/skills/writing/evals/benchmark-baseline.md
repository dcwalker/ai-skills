# Skill Benchmark: writing

**Model**: claude-sonnet-5 (executor), claude-opus-5 (analyzer)
**Date**: 2026-08-13T23:45:00Z
**Evals**: 1–22 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectation Pass Rate | 106/111 (95.5%) |
| Evals Fully Passed | 19/22 |
| Time | 96.8s ± 46.2s |
| Output Tokens | 7943 ± 4080 |
| Errors | 0 |
| Skill invoked | 22/22 trials |

## Per-eval results

| Eval | Scenario | Pass Rate | Time (s) | Tokens |
|------|----------|-----------|----------|--------|
| 1 | Peer email, rung-1 corpus | 6/6 | 85.7 | 6870 |
| 2 | New external recipient, rung-2 substitution | 5/5 | 169.8 | 13631 |
| 3 | No corpus anywhere | 4/5 | 27.2 | 1758 |
| 4 | Audience missing from the request | 4/4 | 7.0 | 262 |
| 5 | Two artifacts, two audiences, one run | 5/5 | 140.6 | 12479 |
| 6 | Rewrite an assistant-sounding draft | 4/4 | 120.0 | 9520 |
| 7 | Explicit skip-the-research override | 4/4 | 10.7 | 578 |
| 8 | Journal entry, audience is self | 4/4 | 95.6 | 7675 |
| 9 | Voice held across two revisions | 5/5 | 89.9 | 6693 |
| 10 | Cache belonging to different accounts | 4/4 | 85.1 | 7133 |
| 11 | Own cache reused and confirmed | 4/4 | 61.6 | 4928 |
| 12 | Blog post from posts on disk | 5/5 | 150.9 | 13092 |
| 13 | Jira comment, display-name collision | 5/5 | 60.8 | 4949 |
| 14 | Slack corpus from an on-disk export | 6/6 | 133.5 | 11420 |
| 15 | General-profile fallback, personal audience | 3/6 | 56.6 | 4001 |
| 16 | Slack corpus through the connector | 6/6 | 80.7 | 6553 |
| 17 | Two-sample corpus, confidence calibration | 5/5 | 144.0 | 11669 |
| 18 | Register mismatch, banter corpus, serious news | 5/5 | 80.2 | 6311 |
| 19 | Revision pushing against the observed voice | 4/5 | 101.6 | 8219 |
| 20 | Stale card plus changed relationship | 6/6 | 154.4 | 13097 |
| 21 | Retired account identifier | 6/6 | 115.8 | 10170 |
| 22 | Collaborative document, authorship by blame | 6/6 | 156.9 | 13735 |

## The five failed expectations

**Eval 3 — a menu instead of a description.** With no corpus at all, the skill's
no-evidence path says to ask the user to describe how the message should sound
in their own words, with a formality menu explicitly ruled out as the primary
ask. The trial opened with "Do you want this brief and direct, or more
detailed/formal?" — a two-option menu. Everything else on that eval passed: the
empty searches were reported, no unevidenced card was presented, and nothing was
written. This is a genuine miss against a rule the skill states plainly.

**Eval 15 — three expectations, all traceable to one environment artifact.** The
fixture's `identity.md` and mailbox both belong to `eval-user@example.com`, but a
trial also inherits the host session's real user identity. The trial compared the
cached identity against the *host's* address, concluded the cache belonged to
someone else, and therefore never used the `general.md` fallback the eval exists
to test. The reasoning it applied was the skill's own identity check, applied to
the wrong signal. Its draft was otherwise careful: no invented arrival time, a
`[time]` placeholder rather than a guess, no work register transplanted onto a
sibling. Fixtures cannot control the host identity, so this eval measures less
than it intends until the harness can present a single unambiguous account.

**Eval 19 — a revision turn that produced no revision.** Turn 2 warmed the draft
correctly, kept the observed mechanics, and imported no boilerplate. Turn 3 asked
for it shorter again, and the reply was "Want it saved as a Gmail draft now, or
any more tweaks?" with no draft at all: the skill edited its cached style card and
answered with housekeeping instead of the artifact. A revision request must
produce a revision.

## Two expectations amended before this baseline was recorded

Both were errors in the eval, not the skill, and both are recorded here rather
than quietly rewritten.

**Eval 8** demanded a `## tomorrow` section in the journal entry. The user gave no
items for it, and the skill says in as many words that filling a section because
the samples always have one is not a reason, and to write the shorter artifact
instead. The trial omitted the section deliberately. The expectation now allows
the omission and grades the header *style* rather than the header list.

**Eval 12** demanded the blog card sit at the highest polish tier. That came from
a line in the source table asserting a tier for blogs, which contradicted Step 5's
rule that the tier is read off the samples. The trial read its samples — fragments,
lowercase asides, dry humour — and recorded Tier 3, which is the correct behaviour.
The skill's assertion has been removed and the expectation now grades the tier
against the samples.

## Findings fixed during the benchmark, before the recorded run

**A draft saved into the mailbox without permission.** The first trial of the
first attempt called `create_draft` and wrote the email into the fixture mailbox.
The skill already said "save a draft only after the user confirms the text", and
the trial announced what it had done rather than concealing it — it read "I will
not be around to answer follow-ups" as standing authorization. That clause appears
in nine of the 22 prompts, so the reading was closed rather than left to chance:
unavailability now authorizes drafting without a confirmation pause and nothing
else, stated in the delivery rules, at the end of Step 7 where the draft is handed
over, and in the quality rules. The whole suite was then re-run from scratch so
every trial in this baseline ran against one skill version. In the recorded run,
all six evals that grade a no-write expectation are clean: zero Gmail drafts, and
Slack and Jira state identical to their seeds.

**Trials could read a real cache outside their isolated HOME.** Three trials (10,
12, 19) read `/root/writing-style/`, left behind by runs that predated the
per-trial `HOME` isolation. Eval 12 was materially affected: its style card was
the stale cached card rather than research it performed. The leftover directory
was removed, the three trials re-run, and the driver now warns when the real home
holds a `writing-style` directory a trial might reach. Isolation reassigns `HOME`,
but the account's real home stays readable and a capable model that notices the
mismatch will look there.

## Notes

- Every trial invoked the skill (`skill_invoked` true in all 22), so no result
  measures the skill's absence. This is checked explicitly because an earlier
  pre-baseline run found the skill silently not triggering on terse prompts.
- Nine prompts carry an "I will not be around to answer follow-ups" clause so a
  single-shot trial produces both the style card and the draft. Evals 4 and 18
  deliberately omit it, since their expected behaviour is to stop and ask.
- Evals 9 and 19 are multi-turn (three turns each), driven through
  `follow_ups` and a resumed session rather than one prompt describing several.
- The corpus is not all email: 8 and 12 read local files, 14 a Slack export on
  disk, 16 the Slack connector, 22 a git-blamed collaborative document, and 13
  Jira comments.
- Trials repeatedly flagged a mismatch between the corpus signature ("Alex
  Reyes") and the host session's account, and handled it by naming the conflict
  rather than picking one silently. That is the desired behaviour, but it is a
  fixture artifact rather than a scenario, and it is the same root cause as eval
  15's three failures.
