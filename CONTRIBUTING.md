# Contributing Guidelines

This document outlines our coding standards, documentation practices, and testing expectations for the skills and plugins in this repo, and for the supporting scripts (e.g. `evals/lib/`) that back them. Skills are written to be usable by any capable agent, not just Claude Code; this repo's plugin packaging (`.claude-plugin/`, the marketplace) is a Claude Code-specific distribution mechanism, but the skill instructions themselves should not assume a specific agent's tool names or behavior.

## Planning

Before diving into implementation, we encourage you to:

- Create a plan for your changes and document it in the project's tracking system
- Have your plan reviewed and confirmed before beginning implementation
- Ensure your work aligns with the project goals defined in the README

This helps ensure we're all moving in the same direction and prevents duplicate effort.

## Coding Standards

### General Principles

- Clarity over cleverness: write code that's easy to understand and maintain. Code should be clear and intentional. Variables, function names, and types should have meaningful names that describe their purpose.
- Brevity over verbosity: be concise, but not at the expense of clarity
- Follow DRY principles: centralize shared logic and avoid duplicating it across skills or scripts
- Security: use environment variables or secure vaults for secrets, API keys, and credentials
- Ecosystem best practices: adhere to community and industry best practices; use the existing patterns and frameworks established in the project.
- Performance and scalability: code should be resource efficient and capable of running at large scale.
- Agent portability: write skill instructions around generic tools and outcomes (e.g. `git`, `gh`) rather than a specific agent's tool-calling interface, so skills remain usable by any capable agent

### Configuration and Environment

- Avoid hard-coding URLs or other environment-specific attributes in scripts
- Keep configuration values and constants centralized (e.g., in `config/` directories or `env.sample`)
- Document environment variables used by scripts where they're consumed (e.g. the eval harness's env vars are documented in [evals/README.md](evals/README.md))
- Bypassing pre-commit hooks is strongly discouraged, they exist as a safety net

### Code Maintenance

- Remove dead code rather than commenting it out; version control preserves history
- Assume backward compatibility is not required unless explicitly stated

### Code Quality

- Keep comments factual and focused on describing the current state
- Maintain a tidy codebase by removing typos, stale comments, misleading names, and unused imports
- Never include personally identifiable information (PII) or sensitive data in the project
- Use git tools like `diff` and `reset` when reverting changes

### Dependencies

- Bundle dependencies locally; avoid loading them dynamically from CDNs or services like unpkg.com
- Prefer updating existing direct dependencies; avoid adding new direct dependencies when possible.
- For security or other updates to transitive (indirect) dependencies, update the direct dependency in package.json that brings in that transitive dependency to a version that depends on the fixed transitive version. Do not add the transitive package as a direct dependency just to pin its version.
  - Example: if a Dependabot PR updates `@types/node` (a dependency of `typescript`), update `typescript` in package.json to a version that requires the newer `@types/node`, rather than adding `@types/node` to package.json.
  - Example: if a PR updates a direct dependency (e.g. `lodash`), update that package's version in package.json as usual.

## Testing

We take testing seriously to maintain code quality:

- Tests should describe specific behavior, read like documentation, and use concrete examples rather than vague statements
- All automated tests and linters must pass before committing
- Respect test coverage thresholds if defined; lowering thresholds should not be used as a workaround
- Avoid disabling or skipping linting rules or tests just to make code pass
- Ensure both tests and documentation accurately reflect the implementation before committing

### Evals

Skills are tested with evals, not unit tests. See [evals/README.md](evals/README.md) for the harness and schema.

- Every skill must ship with an eval suite at `evals/evals.json` (plus `evals/fixtures/`), following the skill-creator schema (`id`, `prompt`, `expected_output`, `expectations`)
- Cover both positive cases (clean scenario, skill should act) and negative cases (ambiguous or invalid scenario, skill should ask or decline); a one-sided eval set trains one-sided behavior
- Run the eval suite for any skill you add or modify, and read the transcripts rather than trusting the grader's verdict blindly
- A new skill needs a `benchmark-baseline.json` established before merge; an existing skill's changes are benchmarked against its current `benchmark-baseline.json`
- If a change to an existing skill lowers its benchmark pass rate, or otherwise regresses behavior relative to `benchmark-baseline.json`, justify the regression in the PR description (what tradeoff was made and why it's acceptable) before it can be accepted. Update `benchmark-baseline.json` only after that regression (or an improvement) has been reviewed and accepted

### Adding or Removing a Skill

A skill's name appears in three places besides its own directory, and they drift
silently because nothing fails when they disagree — the skill still loads, since
skills are discovered from the `skills/` directory on disk. What breaks is the
description a user reads when browsing or installing the plugin. Update all
three in the same PR as the skill itself:

1. `.claude-plugin/marketplace.json` — the `Includes:` list in that plugin's `description`
2. `plugins/<plugin>/.claude-plugin/plugin.json` — the `Includes:` list in its `description`
3. `README.md` — the plugin's bullet under [Plugins](README.md#plugins), and, once a
   baseline exists, a link to `benchmark-baseline.md` under the plugin's heading in
   the Evals section

The check is mechanical: for each plugin, the `Includes:` list in both manifests
must match `ls plugins/<plugin>/skills/` exactly, in the same order. A reviewer
should run that comparison rather than eyeballing it, and a PR that adds a skill
without touching both manifests is incomplete regardless of how good the skill is.

## Commit Messages

Clear commit messages help everyone understand the project's evolution:

- Prefix each commit with the issue or task ID from the branch name (e.g., `[PROJECT-123] Add user authentication`)
- If no issue exists, consider creating one to track the work
- When working on a child task, you may optionally append the parent issue ID for traceability
- Keep commit messages professional; avoid emojis or subjective commentary
- Review all uncommitted changes before committing to ensure the commit is complete and devoid of debug code, temporary changes, and unnecessary clutter
- Check that README, comments, and inline documentation are updated to reflect the changes
- Reference the relevant issue or ticket for major decisions, either in the commit message, an ADR, or an inline comment

## Documentation

Good documentation makes the project accessible to everyone.

### Writing Style

- Prefer specific, quantitative claims over vague superlatives
- Use plain language and say what you mean; be concise, but not at the expense of clarity
- Avoid loaded language and unsupported claims

### README Guidelines

- Keep the README accurate and reflective of the current implementation
- Exclude future plans or historical information
- Organize the README doc in this order:
  - Introduction: state the project's purpose, use cases, what it provides, and list key features (one sentence each)
  - Table of Contents: a navigation aid and an overview of all the content
  - Usage: provide concise instructions and examples for common use cases
  - Installation and Configuration: list required and optional steps with their purpose and examples
  - Technical Details: include architecture diagrams, process flows, and sequence diagrams using Mermaid when helpful

### Accessibility

- All screenshots and images must include descriptive alt text
- Use meaningful link text; describe the destination, not the action (avoid "click here" or "read more")
- Maintain heading hierarchy; do not skip levels (e.g., H1 to H3), as screen readers rely on heading structure for navigation

### When to Split a Section into a Separate Document

Keep content in the README by default. Extract a section into its own file under `docs/` (replacing it with a brief summary and a link) when it meets both of these conditions:

1. The section is large enough to split: it exceeds ~500 words or ~40 lines of content, counting each diagram or screenshot as ~20 lines.
2. The extracted page can stand on its own: the content that would move is itself at least ~300 words or ~20 lines. Avoid creating a linked page that contains only a paragraph or two; the navigation overhead is not worth it.

Apply the "scroll test" as a practical check: if a reader must scroll past a section for several screens before reaching the next one, it is a strong signal to extract it.

GitHub's [About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) documentation notes that a README should only contain information necessary for developers to get started using and contributing to the project, and that longer documentation is best suited for separate pages. It also notes that content beyond 500 KiB will be truncated when viewed on GitHub.

### Additional Documentation

- Avoid new ad-hoc ALL_CAPS doc files. Convention files (README, CONTRIBUTING, AGENTS, SKILL.md) are fine; prefer docs/ or code comments for new documentation.
- Consider maintaining a Glossary of Terms in the README for consistent language across skills and docs
- Update documentation and diagrams whenever the implementation changes; they should always describe the current state
- Present skill output and messages to the user clearly, accessibly, and with a friendly tone

---

Thank you for helping make this project better! If you have questions about these guidelines, please don't hesitate to ask.
