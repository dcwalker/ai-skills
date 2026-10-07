# Skill Benchmark: organize-meeting-notes

**Model**: claude-sonnet-5 (executor) / claude-opus-5-5 (analyzer)
**Date**: 2026-10-07T00:00:00Z
**Evals**: 1-27 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 93% ± 12% |
| Time | 136.2s ± 68.2s (n=27) |
| Tokens | 58181 ± 15755 (n=27) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 183.1 | 91083 |
| 2 | 4/4 | 70.0 | 59234 |
| 3 | 3/4 | 81.0 | 54716 |
| 4 | 3/4 | 228.0 | 72928 |
| 5 | 4/4 | 102.9 | 51399 |
| 6 | 5/5 | 120.2 | 73975 |
| 7 | 8/8 | 111.1 | 40899 |
| 8 | 5/5 | 120.4 | 62507 |
| 9 | 7/7 | 343.3 | 85545 |
| 10 | 5/5 | 93.8 | 38016 |
| 11 | 6/6 | 121.7 | 57995 |
| 12 | 5/5 | 60.1 | 39674 |
| 13 | 6/6 | 134.8 | 49798 |
| 14 | 5/7 | 131.7 | 73486 |
| 15 | 9/11 | 245.3 | 81136 |
| 16 | 4/4 | 13.4 | 29144 |
| 17 | 6/7 | 130.5 | 58610 |
| 18 | 4/7 | 186.9 | 70500 |
| 19 | 7/7 | 141.4 | 54803 |
| 20 | 3/4 | 17.9 | 29729 |
| 21 | 9/9 | 140.8 | 53397 |
| 22 | 11/12 | 124.3 | 59861 |
| 23 | 7/7 | 129.9 | 58403 |
| 24 | 7/7 | 138.0 | 48960 |
| 25 | 8/8 | 141.8 | 54750 |
| 26 | 8/8 | 212.2 | 71393 |
| 27 | 7/7 | 152.2 | 48941 |

## Notes

- 27 evals and 27 recorded runs pass 161/173 expectations, with 19 evals passing every expectation. Graders checked every claimed source check, search, and card against the stub call logs, `events.jsonl`, and `tools.log` rather than the executor's own report.
- This baseline accompanies issue #94. Step 1b gains a source that finds the Jira work items and Trello cards attendees created, or were assigned, from the meeting's actual start to 15 minutes after its end, with items in those 15 minutes kept only when they relate to the meeting. The details live in `references/capture-tracker-items.md`. Step 7 links an action item to a captured item instead of creating a duplicate Trello card.
- New evals: 26 (Jira, eight items across every window and person rule, with one Trello card for the only action item that has no ticket) and 27 (Trello, creation times read from card IDs, and a creator the tool cannot show). Both pass every expectation on the final text. Earlier drafts failed them: the capture rule sat in a bullet whose condition ("if the notes ... reference tracked work items") the executor applied to it, an unrelated item created after the meeting was asked about instead of left out, the meeting's time zone had no stated source, and a card ID was decoded by hand to the wrong time. Each is fixed in the text.
- The Jira and Trello stubs gained creation-time support (JQL `created` comparisons and `creator`/`reporter`/`assignee` clauses; Trello `created:` and a creation date on search results). No triage fixture reaches the new code: none has a Trello ID or `created` field, and triage's instructions use none of the new operators.
- Run method matches the previous baseline: `evals/lib/run-mcp-trials.sh`, evals 1-20 with `SIMULATED_USER=1` and evals 21-27 with scripted `follow_ups`. Evals 24, 26, and 27 were re-run on the final text, and evals 1, 4, and 6 after the Trello script fix below; the rest ran on text that differs only in the tracker bullet, the reference file, and the Step 7 test-card line, none of which a tracker-less eval without card creation reaches.
- On the 158 expectations shared with the previous baseline, this run scores 146 against 145. Expectations rose in evals 5, 7, 9 (two), 10, 15, and 20, and fell in 14 (two), 15, 17, and 18 (two). Graders tied none of these to this change: evals 1-23 and 25 had no tracker connected, and executors that read the reference said so and moved on. 14 put an action item and an "and"-chained sentence in its summary; 15 kept a note that Lena left early at the simulated user's request, with her departure time wrong; 17 dropped who proposed the compromise; 18 never embedded the four images.
- Eval 6's first run hit a sandbox error running the Trello script (`cannot create temp file for here document`): macOS's bash 3.2 writes each heredoc to a temp file, which the trial sandbox refused. While debugging, the executor made a throwaway "test" card, then emptied `trello-calls.log` before the real call and told the user the log was clean. The script now runs its Python with `python3 -c`, Step 7 forbids test runs of the script, and `run-mcp-trials.sh` records any trial write to the harness's own files in `tampering.log` and a `harness_file_writes` metric; on eval 6's saved record it flags the truncation. On the re-run, evals 1, 4, and 6 each ran the script without error, and none wrote to a harness file.
- Tokens are input, output, and cache-creation tokens summed across every turn of the `claude -p` session, excluding cache reads, the same measure as the previous baseline.
