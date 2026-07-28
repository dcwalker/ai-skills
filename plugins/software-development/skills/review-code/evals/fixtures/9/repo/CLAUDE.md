# CLAUDE.md

## Code Standards

- All HTTP handlers must set an explicit request timeout when calling
  downstream services; do not let requests hang indefinitely on a slow
  dependency.
- Prefer `const` over `let` unless reassignment is required.
