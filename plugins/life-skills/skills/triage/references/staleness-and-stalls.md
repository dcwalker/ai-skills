# Staleness and Stalls

Steps 7, 7a and 7b in full. Read this when an item has gone quiet — the
thresholds for when silence is worth raising, how to draft a status comment
that says something true, and the interview that unblocks an item stalled past
30 days. An item with recent activity skips all of it, and closed items are
exempt outright.

## Step 7: Staleness check

Calculate the number of days since the last activity (comment, field update,
status change, or for email, the last message in the thread). Items in a
"Done" or equivalent closed status are exempt.

| Age with no activity | Action |
|---|---|
| 3–7 days | Note it; no action required |
| 8–21 days | Ask: "No updates in N days, want me to draft a status comment or follow-up?" |
| 22+ days | Ask the same; if no clear progress, also offer the stall interview (Step 7b) |

Before trusting the last-activity timestamp, confirm it reflects real
activity. A bulk import, sync, or migration can stamp many items with an
identical timestamp that has nothing to do with when the item was actually
last touched. If several items in the set share a suspiciously identical
timestamp, treat it as unreliable and fall back to content signals instead:
dates mentioned in the description, comment dates, or linked PR/doc activity.

## Step 7a: Draft a status comment or follow-up

Search recent activity on the item and any linked content (PRs, docs, Slack,
prior email threads) to find what has actually happened. Draft a comment or
email that:

- States current status factually
- Notes any blockers or dependencies
- Proposes a specific next action

Show the full draft and get explicit approval before posting or saving.

Use the best available tool to post the comment or save the draft (MCP →
skill → CLI → REST), following the same hierarchy as Step 1. For Jira, if
posting via REST, use ADF format (not plain text):

```bash
curl -s -X POST \
  -u "${ATLASSIAN_USER_EMAIL}:${ATLASSIAN_USER_API_KEY}" \
  -H "Content-Type: application/json" \
  "https://YOUR-SITE.atlassian.net/rest/api/3/issue/{key}/comment" \
  -d '{"body": <ADF doc>}'
```

For Gmail follow-ups, use `create_draft` to save a draft. The Gmail MCP does
not send; surface the saved draft to the user so they can review and send it
themselves in Gmail.

## Step 7b: Stall interview (30+ days, no progress)

If an item has been open for more than 30 days with no meaningful progress,
and the user wants to unblock it, initiate a structured interview using the
`conduct-interview` skill. The goal is one immediately actionable next step.

Frame the interview around:

1. What was the original intent of this item?
2. What has been tried? What was the result?
3. What is blocking progress right now?
4. Can this be broken into smaller pieces? What would the first piece be?
5. Is this still valuable, or should it be closed/deferred?

Ask one question at a time.

Apply LEAN thinking: if the item has no owner, no recent interest, and no
dependency, closing or deferring it is often the right answer.

After the interview, produce:

- A rewritten title if needed
- Child tasks or subtasks for each phase, or a Trello card capture via Step 4c
- A recommended status or list assignment for the parent
- A comment summarizing the review

Confirm all changes before applying.
