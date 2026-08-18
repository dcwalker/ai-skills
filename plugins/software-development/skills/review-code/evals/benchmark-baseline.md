# Skill Benchmark: review-code

**Model**: claude-opus-5
**Date**: 2026-08-18T22:10:00Z
**Evals**: 1-14 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 50/51 (98%) |
| Evals fully passing | 13/14 |
| Time | 103.4s ± 13.6s |
| Tokens | 46,696 ± 1,484 |
| Tool calls | 11.2 ± 1.7 |

Supersedes the 2026-07-31 sonnet baseline (14/14). The single miss is eval 5,
and it is a genuine disagreement about whether that fixture is clean rather
than a sloppy review — see below. Spreads are population standard deviations.

## Per-eval results

| Eval | Scenario | Passed | Time (s) | Tokens | Tool calls |
|------|----------|--------|----------|--------|------------|
| 1 | Missing input validation vs CONTRIBUTING | 5/5 | 97.6 | 45,585 | 10 |
| 2 | No guideline files — fall back, don't skip | 3/3 | 112.5 | 47,878 | 13 |
| 3 | SQL injection, must rate High+ | 4/4 | 110.7 | 46,083 | 11 |
| 4 | Compliant code — don't invent findings | 3/3 | 97.5 | 46,088 | 11 |
| 5 | Guideline carve-outs — don't flag them | **2/3** | 103.4 | 49,482 | 10 |
| 6 | Missing async error handling | 3/3 | 102.8 | 45,290 | 10 |
| 7 | Rate limiter with no window reset | 3/3 | 97.3 | 44,698 | 8 |
| 8 | AGENTS.md — unmasked PAN in logs | 4/4 | 100.8 | 45,395 | 11 |
| 9 | CLAUDE.md — missing downstream timeout | 4/4 | 91.4 | 46,098 | 10 |
| 10 | Unchecked lookup that returns undefined | 3/3 | 89.5 | 46,117 | 11 |
| 11 | One bad file beside a compliant one | 3/3 | 94.5 | 48,632 | 11 |
| 12 | Missing endpoint test, one endpoint has one | 4/4 | 96.2 | 46,706 | 14 |
| 13 | Skill in the diff — Step 4b static only | 5/5 | 146.3 | 49,421 | 14 |
| 14 | Skill in the repo but not in the diff | 4/4 | 107.2 | 46,275 | 13 |

Graded from the review text each trial produced, checked against the fixture
sources. Every workspace was verified untouched afterwards: zero commits in all
fourteen, and the only working-tree changes are the two fixtures' own seeded
edits (13's `SKILL.md` append, 14's `report.js`). `check-trial-hygiene.sh`:
`clean: no session trailers in 14 trial(s)`.

## Eval 5: the skill found something the fixture didn't account for

Fixture 5 is a false-positive trap. `CONTRIBUTING.md` carves out two exceptions
— `any` on a third-party SDK payload that gets narrowed, and TODOs that
reference a ticket — and `webhooks.ts` contains exactly one of each. The
expectation is that a good reviewer respects both and lands in the None/Low
band (0-39).

The trial respected both, explicitly, in a `Checked and deliberately NOT
flagged` block. It still scored **45**, and the expectation fails.

What pushed it over was a finding the fixture does not contemplate:
`handleWebhook` accepts and acts on a webhook body with **no signature or HMAC
verification, no timestamp/replay check, and no shared secret** anywhere in the
tree. `parseSdkEvent` validates the payload's *shape*, but nothing establishes
that it came from the provider, so any party who can reach the endpoint can
trigger notifications for arbitrary order ids. The trial hedged it correctly —
"if verification is done by upstream middleware outside this tree, this is a
non-issue" — and rated it Medium, not High.

Its second Medium is also substantive: the `TODO(PROJ-482)` comment claims
"failures are logged and can be replayed manually", and there is no logging in
the file or in `sendNotification`. The deferral is justified by a control that
does not exist. That finding is about the comment being *false*, not about the
TODO being disallowed — which is why expectation 2 still passes.

**Scored as written: 2/3.** But the question this raises is whether fixture 5 is
actually clean, and that belongs to the eval's owner, not to me. Two ways out:
add signature verification to the fixture so the only remaining observations are
the two carve-outs, or widen the expectation's band and name the webhook-auth
finding as acceptable. Doing neither leaves an eval that a sufficiently careful
reviewer fails for being right.

## Four gaps in the skill's own text, all hit repeatedly

Each of these was reported independently by multiple trials.

**`Bash` is restricted to `gh` only, but local mode cannot work under that
rule.** The Rules say "Allowed tools: `Read`, `Glob`, `Grep`, `Bash` (for `gh`
commands only)", yet Step 1 requires knowing the branch and Step 3's local mode
requires knowing what is in the working tree — neither answerable without `git
status` / `git diff` / `git remote`. Every one of the fourteen trials used `git`,
and at least five flagged the deviation against themselves rather than hiding
it. The rule as written is unfollowable; it should permit read-only `git`.

**The text-output template is PR-shaped.** Its trailing block is headed
`PR Level`, with no local equivalent, so trials substituted `Repository Level`,
`Repo Level` or `Project Level` — three different headings for the same section.
Any grader that string-matches `PR Level` would fail a conformant local review.

**`Repository: owner/repo` is unfillable when there is no remote.** None of these
fixtures configure one. Every trial said so explicitly instead of inventing a
slug, which is the right instinct, but the template gives them nothing to write.

**The Summary tally has no Critical row.** The risk table defines five bands and
the tally template lists only High / Medium / Low. Evals 3, 8, 11 and 14 all
scored Critical and each invented a `🔴 Critical:` row. They agreed on the
format, but the skill should specify it.

A fifth, smaller one: the skill tells trials to wrap issue text "matching the
sonar script style", referencing a script that is not in this repo.

## Fixture observations

- **Fixture 8 has an unintended third defect.** `src/payments.js` calls
  `gateway.charge(...)` but never requires `./gateway`, so every call throws
  `ReferenceError`. Verified against the fixture source. The eval grades the PAN
  logging; the missing import is real and unscored, and the trial reported it as
  a High.
- **Fixture 7 advertises a race that cannot happen.** Its comment says "simulate
  async work where another request could interleave", but `isRateLimited`'s
  read-check-write is fully synchronous, so nothing can interleave under Node's
  event loop. The trial declined to assert the race and flagged the shared state
  on its true grounds — per-process scope, and fragility the moment an `await`
  is introduced. If the eval means to test for a race, the fixture does not
  contain one.
- **No fixture has a working tree diff except 13 and 14.** For the other twelve,
  "review the local working tree" can only mean the whole checked-in tree, since
  everything sits in a single `Initial fixture state` commit. The skill's Step 3
  handles this ("read files from disk") but Step 4 is phrased diff-first ("read
  every changed file"), and eleven trials noted the ambiguity.
- **No fixture ships a cassette**, so `gh pr view` hits the stub's refusal. The
  skill's `2>/dev/null` makes that indistinguishable from a genuine "no PR" —
  correct outcome here, but a misconfigured `gh` would silently degrade to local
  mode the same way.
- `env.sh` exports `SONAR_HOST_URL` / `SONAR_TOKEN` into every trial; this skill
  never uses Sonar. Harmless, noted by six trials as confusing.

## One expectation cannot fail in this environment

Eval 13 expectation 5 requires that no executor/grader subagents were spawned to
run the fixture skill's evals. It passes — but these executors have **no `Agent`
tool**, so it could not have failed regardless of what the skill did. Read it as
untested rather than as evidence. Testing it honestly needs an executor that
*can* spawn agents and chooses not to.

## What the suite establishes

The restraint cases are the valuable half and they hold. Eval 4 scored a fully
compliant fixture at 25 and affirmatively verified all four CONTRIBUTING rules as
met rather than reporting them as gaps. Eval 11 flagged `reactions.js` at
Critical while stating that `comments.js` "already shows the correct pattern".
Eval 12 flagged the untested endpoint and named the test file covering the other
one. Eval 14 declined Step 4b on a repo that contains a skill the diff does not
touch, reasoning it out loud. Eval 5 is the only miss, and it over-reported by
one band on a finding that is arguably real.

Guideline loading is exact: CONTRIBUTING.md, AGENTS.md and CLAUDE.md were each
picked up by the eval that plants them, and every trial enumerated the full
Step 2 candidate list and reported which were absent.

## Notes

- with_skill only, no without_skill arm: `review-code` is a workflow skill.
- All 14 evals run in local mode. PR mode — posting inline comments, the
  verdict, and the `RISK-LEVEL:` marker — is untested by this suite, which is a
  coverage gap given how much of SKILL.md is devoted to it.
- No harness config was needed; these fixtures need neither `repo` nor
  `delegates_to`.
