---
name: organize-meeting-notes
description: Clean up and structure meeting notes for a personal journal with strict formatting, guided questioning, and staged approval. Use when the user asks to organize, polish, or journalize meeting notes.
metadata:
  category: life-skills
---

# Organize Meeting Notes

Clean and organize raw meeting notes into a journal-ready Markdown format with this final order:
1. Meeting metadata
2. Attendees
3. Notes
4. Action items

## When to Use

Use this skill when:
- The user asks to clean up, organize, or rewrite meeting notes
- The user wants notes converted into a personal journal format
- The user wants guided clarification of note significance before finalizing

## Instructions

### Step 1: Gather Inputs

Collect:
- Meeting title/topic
- Start time
- End time
- Duration
- Location (optional)
- Attendee emails/names
- Raw notes text
- Any screenshots/photos and URLs

If required information is missing, ask for clarification. Do not guess.

### Step 1b: Enrich from Available Sources

Before the interview, check which context sources the current session can
actually reach (a calendar, email, team chat, a ticket tracker, web
fetching). Use only what is genuinely available: skip anything that is not
connected without comment, and never present content as coming from a source
that was not actually consulted. The user may also paste source material
(a calendar event, chat excerpts, an email) directly; treat that the same
way as fetched content.

For each available source:

- **Calendar**: find the event matching the meeting title and time. Pull the
  agenda or event description and the invitee list (cross-check it against
  the attendees from Step 1). Compare the scheduled start/end against the
  actual times: note whether the meeting started and ended on time, ended
  early, or ran long, and by how much (see Step 2 for where this lands).
- **Team chat**: look for messages sent by attendees during the meeting's
  start-to-end window. Judge relevance before proposing anything: a message
  matters only if it bears on the meeting topic (a shared link, a decision
  echoed in a channel, a side answer to a question raised in the room).
  Ignore unrelated chatter.
- **Email**: look for threads involving the attendees or matching the
  meeting topic close to the meeting date (an agenda sent beforehand, a
  document circulated for the meeting, a follow-up thread).
- **Shared links**: collect URLs from the raw notes and from any relevant
  chat or email found above. Follow each link, and summarize in one or two
  sentences what it contains and why it mattered to this meeting. If a link
  cannot be fetched, say so rather than guessing at its content.
- **Ticket tracker**: if the notes or discussion reference tracked work
  items (an item key, or a topic recognizable as a tracked item), look them
  up and capture the item's current summary and status so the note can name
  what was actually discussed.

Present what was found as proposals, source by source, before or during the
Step 4 interview; the user decides what gets in. Enrichment supplements the
user's notes; it never overrides what the user said, and a conflict between
a source and the user's notes is a question to ask, not a correction to
apply silently.

### Step 2: Format Meeting Metadata

Format metadata exactly as:
- Meeting title/topic as `##` (H2)
- Remaining metadata on one line, fields separated by `•`
- Field order: `Start:`, `End:`, `Duration:`, `Location:` (only include location if provided)
- Keep labels (`Start:`, `End:`, `Duration:`, `Location:`) non-bold
- Bold only the values

Time correction rule:
- If end-start matches duration, keep end time as-is.
- If not, strikethrough only the original end time value and append corrected end time value (start + duration), both in the `End:` field.
- Example mismatch pattern:
  `Start: **Feb 27, 2025 at 11:00 AM** • End: ~~11:30 AM~~ **11:07 AM** • Duration: **7 minutes** • Location: **Home**`
- Example match pattern:
  `Start: **Feb 27, 2025 at 11:00 AM** • End: **11:30 AM** • Duration: **30 minutes**`

Schedule note (only when calendar data is available from Step 1b):
- Compare the actual start/end against the calendar event's scheduled times
  and propose one italic line directly under the metadata line stating how
  the meeting tracked its schedule, with the difference in minutes.
- Example: `*Scheduled for 30 minutes; ran 12 minutes long.*`
- Example: `*Started 5 minutes late; ended on time.*`
- Include it only with the user's approval, and omit it entirely when no
  calendar data exists; never estimate schedule adherence without the
  scheduled times.

### Step 3: Format Attendees

Transform attendee emails:
- Email patterns: `<first>.<last>@...` or `<initial>.<last>@...`
- Convert to title case names
- Remove `-contractor` from names
- Sort alphabetically by first name
- Output as plain lines (no bullets, no extra formatting)

If only an initial is available and the full first name is unknown, ask the user before finalizing.

Ask the user who did not attend. After response:
- Apply strikethrough to invited names that did not attend.

### Step 4: Interview for Significance (Notes)

This is the most important step. **Every line** of the raw notes must be reviewed in a back-and-forth interview process with the user. Do not skip any line, even if it seems self-explanatory.

If the raw notes contain N lines, you must ask at least N clarifying questions (one per line). Do not batch multiple lines into a single question.

Process:
- Go through each note line one at a time, in order.
- For each line, ask a single clarifying question about its meaning, significance, or context.
- Wait for the user's response before moving to the next line.
- Use the user's response to expand, clarify, or refine that note into a complete, clear sentence.
- Ask for clarification when details are missing. Do not infer missing facts.
- When paraphrasing, always ask for confirmation before moving on.
- The goal is to capture not just facts but also: action items, events/experiences, and information that is important to not forget.
- Each note should become a complete sentence that stands on its own.
- Preserve the user's original tone, word choice, and writing style. Do not sanitize or make the language generic.
- Avoid repetition and filler language.

### Step 5: Clean and Normalize Notes

After the interview is complete, apply these normalization rules:

Name rules in notes:
- Use attendee names as source of truth for spelling.
- First mention of each person: full name.
- Later mentions: first name only, unless multiple attendees share the same first name.

Acronym rule:
- Spell out acronyms on first use.

URL rule:
- If URLs are listed at the end of notes, move them into relevant note locations as Markdown hyperlinks.
- For each link summarized in Step 1b, append its one-to-two-sentence
  summary (what it contains and why it mattered to the meeting) to the note
  that carries the link, subject to the user's approval.

Tracked work item rule:
- Where Step 1b resolved a referenced work item, name it in the relevant
  note with its item key and current summary/status as a Markdown link when
  a URL is known (e.g. `[KEY-123](...): <summary> (<status>)`), so the note
  stands on its own without the tracker open.

Image rule:
- For each screenshot/photo, ask the user for a caption describing its significance.
- Add the caption under each image using italic text (e.g., `*Caption describing the image*`).
- Interlace images into the notes content based on their captions and context (place each image near the related note).
- Use image timestamps (from file name or EXIF data) to ensure images are always presented in chronological order.

### Step 6: Format Notes as Bulleted List

After the interview and normalization, format the notes section as a bulleted list:
- Each note is a bullet point (`- `) containing a complete sentence.
- Images should be interlaced at the appropriate position among the bullets based on their chronological timestamp and contextual relevance.

### Step 7: Staged Approval Workflow

1. Propose updates to:
   - Meeting Metadata
   - Attendees
   - Notes
2. Wait for user approval that these are good.
3. Then identify action items from notes and format as a simple checklist bullet list:
   - Markdown format: `- [ ] ...`
   - No sub-sections
4. Present action items draft for review. Ask: "Are these action items correct?"
5. It is valid for a meeting to have no action items. If none exist, explicitly confirm this with the user.
6. Once action items are confirmed, ask whether to create Trello tasks (one per action item).
7. If user says yes, create one Trello card per action item:
   - Run: `create-trello-task.sh "<action item text>"`
   - Include `--desc` for every Trello card with source context.
   - Minimum required description context: meeting title plus meeting date/time.
   - Preferred additional context: meeting topic and a short reason the action item exists.
   - After each card is created, capture the returned card URL and replace that checklist item's text with a Markdown link to the card.
   - Use format: `- [ ] [Action item text](https://trello.com/c/...)`
8. If no action items are confirmed, skip Trello creation.
9. After Trello creation (or skip), produce final Markdown document.

### Step 8: Final Output Format

When approved, return final Markdown with:
- Metadata block first (title + metadata line)
- Then `###### Attendees`
- Then `###### Notes`
- Then `###### Action Items`

If notes are significantly long:
- Add a concise italicized summary at the top.

At the very end, append:
- `#### YYYY-MM-DD HH:MM: <Meeting Title>`
- Use 24-hour time.

## Quality Rules

- Keep output concise and readable.
- Preserve factual accuracy; do not invent details.
- Ask clarifying questions when uncertain.
- Follow requested section order and formatting exactly.
- Enrichment content must trace to a real source that was actually
  consulted (or material the user pasted). When no context sources are
  available, proceed with the user's notes alone; never simulate a source
  check or fabricate agenda, chat, email, link, or work item detail.
