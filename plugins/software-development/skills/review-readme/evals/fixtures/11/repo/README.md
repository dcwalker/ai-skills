# Wordwall

A small internal announcement board.

## Overview

Wordwall is a small application that lets a team publish short internal announcements to a shared board. It was originally built as a weekend project to replace an unwieldy email thread that nobody could keep track of, and it has slowly grown a handful of features since then, including tagging, search, and a very basic notification system that pings a Slack channel whenever a new announcement is posted, which turned out to be more useful than expected. Under the hood it runs a small Node.js HTTP server that serves a handful of static pages and a couple of JSON endpoints for creating and listing announcements, and it stores everything in a single SQLite file on disk rather than a full database server, which keeps local development simple but does mean it is not meant to be run with more than a few concurrent writers at a time. The configuration is intentionally minimal: a single environment variable controls the port the server listens on, and everything else -- the database file location, the Slack webhook URL, the maximum announcement length -- is hard-coded in a constants file near the top of the entry point so that anyone new to the codebase can find all of the tunable values in one place without hunting through multiple modules. Deployment is handled by copying the repository to a small VM and running the server under a process supervisor, since the traffic volume has never justified anything more elaborate, and the team has generally preferred to keep the operational surface area as small as possible rather than introduce containers, orchestration, or a managed database for what is ultimately a low-traffic internal tool. Testing covers the core announcement creation and listing logic along with basic input validation, but does not currently cover the Slack notification path, which is instead verified manually by posting a test announcement to a staging channel before any release that touches that code, a gap the team is aware of and intends to close eventually but has not yet prioritized given the tool's low blast radius. If you are new to the project, the best way to get oriented is to read through server.js from top to bottom, since it is still small enough that the whole request lifecycle -- from receiving a POST, validating the payload, writing to SQLite, and firing the Slack webhook -- fits in a single file and can be understood in one sitting without jumping between many modules.

## Installation

```bash
npm install
```

## Usage

```bash
npm run dev
```

## Testing

```bash
npm test
```

## License

MIT
