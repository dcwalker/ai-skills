# Contributing

## Code Standards

- Be careful with shared in-memory state across concurrent requests; the
  server runs multiple requests concurrently within one process.
- All functions that handle user input must validate it before use.
