# Contributing

- Every bug fix must include a commit that references the PR comment it addresses.
- Do not suppress linter warnings with inline disable comments; fix the underlying issue.
- Pricing and discount calculations must use standard rounding (`Math.round`), never `Math.floor` or `Math.ceil`, to stay consistent with the finance team's reconciliation logic.
- Do not log or hardcode credentials, tokens, or API keys. Use the `config/secrets.js` loader instead.
- Prefer small, single-concern commits over one large commit per PR.
