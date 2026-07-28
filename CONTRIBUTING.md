# Contributing Guidelines

This document outlines our coding standards, documentation practices, and testing expectations to help maintain consistency and quality across the codebase.

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
- Follow DRY principles: centralize shared logic and prefer reusable CSS classes over inline styles
- Security: use environment variables or secure vaults for secrets, API keys, and credentials
- Ecosystem best practices: adhere to community and industry best practices; use the existing patterns and frameworks established in the project.
- Performance and scalability: code should be resource efficient and capable of running at large scale.

### Configuration and Environment

- Avoid hard-coding URLs or other environment-specific attributes
- Keep configuration values and constants centralized (e.g., in `config/` directories or `env.sample`)
- Document all environment variables in a table within the README
- Bypassing pre-commit hooks is strongly discouraged, they exist as a safety net

### API Integration

When working with external APIs:

- Consult official API documentation before writing or modifying integration code
- If you can't find documentation, please ask for the specification or reference material
- Avoid relying on trial-and-error approaches

### Code Maintenance

- Remove dead code rather than commenting it out; version control preserves history
- Assume backward compatibility is not required unless explicitly stated
- Design with a mobile-first approach and architect APIs before UIs when possible
- Favor lightweight user interfaces with centralized business logic

### Code Quality

- Keep comments factual and focused on describing the current state
- Maintain a tidy codebase by removing typos, stale comments, misleading names, and unused imports
- Never include personally identifiable information (PII) or sensitive data in the project
- Use git tools like `diff` and `reset` when reverting changes

### Accessibility

- Use semantic HTML elements (`<button>`, `<nav>`, `<main>`, etc.) rather than generic `<div>` or `<span>` with click handlers
- Ensure sufficient color contrast (WCAG AA minimum is 4.5:1 for body text, and 3:1 for large text)
- Never rely on color alone to convey meaning; pair it with text, icons, or patterns
- All interactive elements must be keyboard-navigable and have visible focus states
- Use ARIA labels and roles only when semantic HTML is insufficient; do not layer ARIA on top of already-semantic elements

### Dependencies

- Bundle dependencies locally; avoid loading them dynamically from CDNs or services like unpkg.com
- Prefer updating existing direct dependencies; avoid adding new direct dependencies when possible.
- For security or other updates to transitive (indirect) dependencies, update the direct dependency in package.json that brings in that transitive dependency to a version that depends on the fixed transitive version. Do not add the transitive package as a direct dependency just to pin its version.
  - Example: if a Dependabot PR updates `@types/node` (a dependency of `typescript`), update `typescript` in package.json to a version that requires the newer `@types/node`, rather than adding `@types/node` to package.json.
  - Example: if a PR updates a direct dependency (e.g. `lodash`), update that package's version in package.json as usual.

### Logging

When adding logging to the application, always include useful messages with context that will enable future troubleshooting. Log outcomes and results, not plans or progress. Use these standard levels:

TRACE
Ultra-detailed diagnostic information including fine-grained internal state, step-by-step operations, and verbose algorithm flow. Typically only enabled during deep debugging.

DEBUG
Developer-oriented diagnostics with useful checkpoints, variable values, decisions, and execution flow that aid debugging but aren't needed during normal operation.

INFO
High-level operational events describing normal behavior, such as starting or completing a task, handling a request, or performing a scheduled operation.

WARN
Unusual or unexpected behavior that didn't stop execution. Something may require attention, but the system continued running successfully.

ERROR
A failure that prevented a task or invocation from completing normally. This includes exceptions, failed API calls, or unrecoverable conditions.

FATAL
A severe failure that stops execution and requires immediate attention.

### Error Handling

- Handle errors gracefully; avoid letting unhandled exceptions crash the application or silently swallow failures
- Classify errors as transient (rate limits, timeouts, and 5xx responses) or non-transient (auth failures, configuration errors, and not found)
- Transient errors should be logged and retried with an appropriate backoff strategy. If retries are exhausted, escalate by logging at ERROR level and surfacing the failure
- Non-transient errors should be logged and raised immediately; retrying these is unlikely to help

## Testing

We take testing seriously to maintain code quality:

- Tests should describe specific behavior, read like documentation, and use concrete examples rather than vague statements
- All automated tests and linters must pass before committing
- Respect test coverage thresholds if defined; lowering thresholds should not be used as a workaround
- Avoid disabling or skipping linting rules or tests just to make code pass
- Ensure both tests and documentation accurately reflect the implementation before committing

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
  - Operations: cover common failure modes and how to resolve them. If the project produces logs, document where they are written, any tools required to read them, the structure of log messages (and file layout if logs are written to disk), and examples of filtering for common scenarios. If the platform does not enforce a log format, define one in the project so log output is consistent and parseable. Document any automated alerting (what triggers an alert, who is notified, and how) and how to monitor the health of the system (health check endpoints, dashboards, status commands, or other observability tools)
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
- If the project requires permissions, maintain a Permissions section in the README describing each one, what access it grants, which features depend on it, and link to official documentation
- Consider maintaining a Glossary of Terms in the README for consistent language across code and UI
- Update documentation and diagrams whenever the implementation changes; they should always describe the current state
- If the project has API endpoints available, then maintain a detailed `openapi.yaml` or `openapi.json` doc in the project
- Include a Design Guidelines section in the README describing color, style, and interaction patterns to keep the UI consistent
- Present user interactions and notifications clearly, accessibly, and with a friendly tone
- Adopt local UI cues and behaviors so the app blends seamlessly into its environment

---

Thank you for helping make this project better! If you have questions about these guidelines, please don't hesitate to ask.
