# Contributing

## Code Standards

- All functions that handle user input (request bodies, query params, form
  fields) must validate that input before using it. Reject or sanitize
  invalid input; never pass it straight through to a database call, shell
  command, or downstream service.
- Prefer async/await over raw promise chains.
- Keep functions under ~40 lines where practical.
