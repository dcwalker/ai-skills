# Session Service

A small session/connection management service used for eval fixtures.

## Operations

### Logs

Application logs are written to `logs/app.log`, one entry per line, formatted as:

`<ISO8601 timestamp> <LEVEL> [<component>] <message>`

To view the last 24 hours of logs locally:

    cat logs/app.log

Levels used: INFO, WARN, ERROR, FATAL.
