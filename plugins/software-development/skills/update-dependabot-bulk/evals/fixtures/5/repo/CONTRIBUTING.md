# Contributing

- Never add a transitive dependency directly to `dependencies`, `devDependencies`,
  or `resolutions`. Update the direct dependency that pulls it in instead.
- Run `yarn install`, tests, and `knip` after any dependency bump before committing.
- Flag major-version bumps for review instead of applying them silently -- they
  often carry breaking changes.
- Do not bypass pre-commit hooks.
