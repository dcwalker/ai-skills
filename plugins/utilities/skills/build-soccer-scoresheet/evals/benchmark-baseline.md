# Skill Benchmark: build-soccer-scoresheet

**Executor**: claude-opus-5-5 (Agent-tool subagents)
**Grader**: claude-opus-5-5
**Date**: 2026-10-16
**Evals**: 1-6 (1 run each, with and without the skill)
**Fixtures**: `python3 evals/build_fixtures.py` (needs Pillow)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Expectations passed | 44/44 (100%) | 17/44 (39%) | +27 |
| Evals fully passing | 6/6 | 1/6 | +5 |
| Time | 61.1s ± 36.8s | 41.4s ± 25.4s | +19.7s |
| Tokens | 83,516 ± 9,337 | 70,184 ± 6,768 | +13,332 |

`benchmark-baseline.json` holds the with-skill runs only. The without-skill
runs for evals 1-4 come from the first iteration, whose inputs were the same;
evals 5 and 6 were rerun after their fixtures changed. With-skill evals 1
and 6 were rerun after the rule that screenshots never appear in the report
was added; the new expectation was graded on the existing without-skill
outputs, which also left screenshots out.

Each trial is one Agent-tool subagent working in a copy of
`fixtures/<id>/inputs`, with no browser, web, calendar, email, or connector
access, so every fact has to come from the inputs. Wall-clock times in the
fixtures sit mid-minute so each expected minute is unambiguous.

## Per eval

| Eval | Case | With | Without |
|------|------|------|---------|
| 1 | World Cup final: screenshots, watch, notes, photos, extra time, shootout | 13/13 | 4/13 |
| 2 | No second-half anchor: estimate and ask | 4/4 | 2/4 |
| 3 | Substitute coach, absent player, no opponent roster, saved penalty | 8/8 | 1/8 |
| 4 | Club tournament with unknown period length: ask | 3/3 | 3/3 |
| 5 | Team app result vs Veo AI tags | 6/6 | 3/6 |
| 6 | Journal export with written minutes and shorthand | 10/10 | 4/10 |

## What the evals found

- **Stoppage time is where runs without the skill fail.** They found the
  right regular-time minutes but wrote halftime and full time as `45+'` and
  `90+'`, or left them out, and none followed the report template, sorted
  rosters by number, embedded photos, or kept empty sections with a plain
  statement.
- **Eval 4 does not discriminate.** Both configurations asked for the period
  length instead of guessing.
- **Real notes changed the skill.** A sample of real sideline notes was a
  journal export: one entry per event, UTC times with a zone name, escaped
  Markdown, a minute written from a watch, first names, "us" and "them", and
  a card after the final whistle. Eval 6 reproduces that shape with public
  World Cup content. The skill now treats written minutes as anchors,
  resolves disagreeing minutes across sources and asks when they stay
  unresolved, writes team names instead of us and them, and adds
  Post-match lines.
- **Screenshots stay out of the report.** They are read for the clock, the
  score, and who scored, and only game photos are embedded; evals 1 and 6
  check this.
- **A real game refined the timing rules.** Hand-started tracker clocks ran
  7 to 16 seconds behind the recording's kickoff, by a different amount each
  half, and two events landed within seconds of a minute boundary. The skill
  now ranks recording times above tracker clocks, uses Veo's Kickoff events
  as period anchors, and asks when sources split at a boundary. All six
  with-skill evals were rerun after those changes.
- **Minutes come from a script.** One run put a halftime at `45+11'` instead
  of `45+6'` by adding a recording's lead time twice. The skill now converts
  every time with `scripts/game_minutes.py`, which also flags events within
  seconds of a minute boundary.
- **A missing opponent roster is stated, not asked about.** Parents
  rarely have one, so the skill writes `No opponent roster` and says so in
  the reply; an earlier run of eval 6 asked instead.
- **Photos carry captions, and written minutes beat note timestamps.** Each
  photo has its own `📷 Photo` line with an italic caption directly below
  the image, and when a note's written
  minute and its own timestamp disagree, the written minute is used without
  asking (a tracker screenshot or recording still outranks it).
- **Not exercised**: reading jersey numbers from a recording to fill a gap.
  Trials have no recording access.
