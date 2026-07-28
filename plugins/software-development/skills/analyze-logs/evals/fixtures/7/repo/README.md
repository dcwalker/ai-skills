# Fetchly

A small internal service used for eval fixtures.

## Operations

### Logs

Logs are aggregated centrally and must be pulled with the bundled fetch script,
which handles authentication against the log aggregator automatically. Do not
read log files directly from disk.

Fetch the last 24 hours of logs with:

    scripts/fetch-logs.sh --since 24h

This writes the fetched logs to `logs/app.log`.
