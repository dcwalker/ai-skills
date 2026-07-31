# Contributing

## Code Standards

- All functions handling user input must validate it before use.
- Errors must never be silently swallowed; log or rethrow.

## Skills

Skill definitions live under `plugins/<plugin>/skills/<skill>/`. Every skill
ships a `SKILL.md` (kept under ~500 lines), an `evals/evals.json` suite, and a
committed `evals/benchmark-baseline.json` recording the last approved run.

## Evals

Run the eval suite for any skill you modify before merging, and keep the
checked-in benchmark baseline up to date.
