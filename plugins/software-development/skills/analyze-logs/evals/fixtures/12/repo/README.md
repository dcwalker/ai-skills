# Multi-Env Service

A service deployed to multiple environments, used for eval fixtures.

## Operations

### Logs

Application logs are written per-environment, one entry per line, formatted as:

`<ISO8601 timestamp> <LEVEL> [<component>] <message>`

To view the last 24 hours of logs locally:

    cat logs/staging.log       # staging environment
    cat logs/production.log    # production environment
