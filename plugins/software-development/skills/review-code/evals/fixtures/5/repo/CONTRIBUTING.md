# Contributing

## Code Standards

- `any` is acceptable when typing the raw response from a third-party SDK,
  as long as the value is validated and narrowed to a concrete type before
  it is used anywhere else in the function. Do not use `any` elsewhere.
- TODO comments are fine when they reference a tracked ticket (e.g.
  `TODO(PROJ-123): ...`) for planned, non-blocking follow-up work. Do not
  leave untracked or vague TODOs.
- All functions that handle user input must validate it before use.
