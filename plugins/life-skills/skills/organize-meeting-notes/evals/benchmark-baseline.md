# Skill Benchmark: organize-meeting-notes

**Model**: claude-sonnet-5 (executor) / claude-opus-5 (analyzer)
**Date**: 2026-08-18T21:24:20Z
**Evals**: 1-14 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 151.6s ± 47.9s (n=14) |
| Tokens | 60343 ± 6294 (n=14) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 136.1 | 61359 |
| 2 | 4/4 | 106.2 | 50743 |
| 3 | 4/4 | 127.9 | 57090 |
| 4 | 4/4 | 142.0 | 63209 |
| 5 | 4/4 | 85.0 | 51576 |
| 6 | 4/4 | 137.2 | 58587 |
| 7 | 6/6 | 237.6 | 69760 |
| 8 | 5/5 | 136.8 | 61522 |
| 9 | 6/6 | 265.0 | 73023 |
| 10 | 5/5 | 128.9 | 59495 |
| 11 | 6/6 | 181.6 | 64622 |
| 12 | 5/5 | 137.2 | 58723 |
| 13 | 6/6 | 142.1 | 53363 |
| 14 | 6/6 | 158.7 | 61724 |

## Notes

- 14/14 evals pass 70/70 expectations. Results were verified against ground truth rather than executor self-report: every card URL in a final document was byte-compared against `trello-calls.log`, and the ten trials expected to make no calls were confirmed to have produced no log at all.
- This baseline accompanies the summary/sections/quotes/images change: the Step 8 summary rule (measured by ~500 words or ~40 lines, or three or more topic sections, with images excluded from the measurement), the Step 5 topic rule (bold label lines when a meeting had three or more clear topics), the Step 5 quote rule (verbatim inline fragments and one blockquote pull quote per section, transcript-gated), and the rewritten image rule (alt text, content-and-timestamp placement, content winning conflicts, ask when undated).
- Evals 1-8 re-ran against the changed skill with no regressions; the four new gated behaviors correctly stayed off in all eight, each trial reporting the length measurement that justified declining a summary.
- Evals 9-14 are new and cover both sides of each trigger: eval 9 (five sections plus a summary at 716 words), eval 14 (the section trigger alone at 108 words, under both length thresholds), eval 10 (a two-line standup that earns neither), eval 11 (one verbatim pull quote from a real transcript, with a generically labeled speaker the skill must ask about), eval 12 (quotes requested with no transcript available), and eval 13 (screenshot placement, plus the image exclusion that keeps four images from manufacturing a summary).
- Two trials were re-run and only the clean runs are recorded here (`run_number` 2 in the JSON). Eval 6's first trial read its `trello-fixture.json` before invoking the script; the URL it used was genuine and logged, but foreknowledge of a fixture taints the trial, so it was re-run under an explicit no-fixture-reads instruction. Eval 9's first trial exposed a fixture defect rather than a skill defect: twenty raw note lines expanded to only 387 words, under the summary threshold, so the executor correctly declined a summary and the eval could not exercise the path it existed to test. The fixture was lengthened to thirty lines across five topics rather than the rule loosened.
- Eval 13 was also re-run (`run_number` 2) after the summary rule changed to exclude images from the measurement. Its first run added a summary off an 87-line measurement that counted four images at ~20 lines each; the graded expectation now requires no summary, which the re-run satisfied.
- Time and token figures are subagent totals from the trial agents' usage reporting, comparable to other subagent-based baselines in this repo. Both rose against the previous baseline (45393 ± 2913 tokens, 88.5 ± 19.9s over 8 evals), driven by the longer fixtures: eval 9 alone interviews thirty note lines.
