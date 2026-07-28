# Contributing

## Code Standards

- All async functions that call external services (network, database, file
  system) must catch and log errors. Do not let unhandled rejections
  propagate to the caller without at least a log statement identifying what
  failed.
