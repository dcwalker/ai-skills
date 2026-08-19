# Field Guidance

How to calibrate a title, a description and a label set to the item in front of
you. Step 4 carries the rules that always apply — propose once, confirm before
writing, never invent. This file carries the worked examples: what "good" looks
like for a personal chore versus a professional bug versus a project, which is
the part that changes with the item.

## Title / subject

A good title is action-oriented and specific enough to act on without reading
the description. Calibrate the phrasing to the context:

- **Personal task:** Use natural language. "Book flights for Austin trip" is
  better than "Flight booking" or "Book flights (acceptance criteria: ...)".
- **Professional task/bug:** Lead with the outcome. "Fix unexpected logout after
  30 min inactivity on mobile" beats "auth bug".
- **Project/initiative:** State the end goal. "Launch self-serve billing portal
  for SMB customers" beats "billing portal".
- **Email captured as an action:** When converting an email into a tracked
  action (a Trello card, a Jira issue, or a stored email action label), set
  the title or subject line to the next action verb, not the original email
  subject. "Reply to Sue with Q3 forecast" beats "FW: Q3 numbers".

For personal items with no description to draw from, ask a brief question
rather than guessing.

## Description

A description should answer: what needs to be done, why it matters, what done
looks like, and any constraints. Calibrate to the context:

- **Personal small task:** A single sentence is often enough. No need for formal
  sections or headers.
- **Personal project:** Key details relevant to the domain. For a trip, that
  means destination, dates, budget, who's going. For a home project, scope,
  materials, and timeline. Write as plain prose, no section headers.
- **Professional task or bug (Tier 2):** A short paragraph covering what needs
  doing, why it matters, and what a completed state looks like, written as
  prose, not as named sections. Only use structured headers (e.g. "Acceptance
  criteria") for Tier 3 items where the complexity genuinely warrants them.
- **Professional initiative/epic (Tier 3):** Full context including stakeholders,
  success metrics, and known constraints. Structured sections are appropriate here.

Capture and forwarding automations often duplicate content, for example a
cleaned summary followed by a repeated "original message" block, or a
forwarded quote chain. Check for this and propose a de-duplicated version
rather than preserving redundant copies.

## Labels / tags

Propose labels that will help find the item later. Calibrate to context:

- **Personal:** Simple tags like "travel", "home", "health", "finance".
- **Professional:** Domain ("auth", "billing"), type ("bug", "feature",
  "tech-debt"), and specifics ("mobile", "ios", "android"). Prefer specific
  over generic when both apply.
- **Email:** Use plain label names with no prefix character. The core action
  labels are `Action`, `Waiting For`, and optionally `Read-Review` and
  `To-Print`. Reference labels are topical (person, project, domain).
