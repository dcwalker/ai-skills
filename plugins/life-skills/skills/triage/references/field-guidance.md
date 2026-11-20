# Field Guidance

How to calibrate a label set to the item in front of you, and what triage adds
to create-task's title and description rules. Step 7 carries the rules that
always apply: propose once, confirm before writing, never invent.

## Title / subject and description

What a good title and description look like, calibrated to a personal chore,
a professional bug, a project, an email captured as an action, a check-in,
and a task tied to a place, is in the create-task skill (its Steps 2 to 4).
Triage applies those rules and adds only this:

- For personal items with no description to draw from, ask a brief question
  rather than guessing.
- A description built by a capture or forwarding automation gets the
  de-duplication check below before any rewrite.

Capture and forwarding automations often duplicate content, for example a
cleaned summary followed by a repeated "original message" block, or a
forwarded quote chain. Check for this and propose a de-duplicated version
rather than preserving redundant copies.

## Labels / tags

Propose labels that will help find the item later, chosen from the labels the
scope already has (SKILL.md Step 0c). Calibrate the choice to context:

- **Personal:** Simple topical labels like "travel", "home", "health",
  "finance", when the board has them.
- **Professional:** Domain ("auth", "billing"), type ("bug", "feature",
  "tech-debt"), and specifics ("mobile", "ios", "android"), from the project's
  labels in use. Prefer specific over generic when both apply.
- **Email:** The account's own labels. When sift-email's rubric exists, its
  Labels table says which label a thread gets; follow it, and flag a thread
  whose current label disagrees with it.

A label the set lacks is never proposed for one item. When three or more
items share a pattern no label covers, SKILL.md Step 9b offers one new label
for them, once.
