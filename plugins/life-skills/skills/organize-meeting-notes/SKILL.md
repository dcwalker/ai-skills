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
- Meeting transcript, if one exists (optional)
- Any screenshots/photos and URLs

If required information is missing, ask for clarification. Do not guess.

A transcript, when provided, is source material for quotes and for
clarifying what was said. It does not replace the raw notes, and it does not
replace the Step 4 interview.

### Step 1b: Enrich from Available Sources

Before the interview, check which context sources the current session can
actually reach (a calendar, email, team chat, a ticket tracker, web
fetching). Use only what is genuinely available: skip anything that is not
connected without comment, and never present content as coming from a source
that was not actually consulted. The user may also paste source material
(a calendar event, chat excerpts, an email, a meeting transcript) directly;
treat that the same way as fetched content.

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

When a transcript was provided, use it to inform the interview: ground each
question in what the transcript shows was said about that line, and note the
statements worth quoting as you go (see the quote rule in Step 5). The
transcript sharpens the questions; it does not answer them for the user.

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

Unanchored enrichment rule:
- A link or work item surfaced by Step 1b may have no matching note to
  attach to (it came from chat, email, or discussion the raw notes never
  mentioned). Propose a new note bullet for it, placed where it fits the
  flow of the meeting, subject to the user's approval; if the user declines,
  drop it rather than forcing it into an unrelated note.

Topic rule:
- Judge whether the meeting covered clear topics. A topic is clear when
  several notes share a subject the meeting itself treated as a distinct
  agenda item, discussion, or decision, not merely a theme visible in
  hindsight.
- Divide the notes into sections when three or more clear topics exist.
  Below that, keep a single flat list.
- Name each section in the meeting's own language (the agenda item, or the
  words the attendees used), and keep the name to a few words.
- Order sections by when each topic came up, and keep the notes within a
  section in their original order.
- Every note belongs to exactly one section. If a note fits none of them, ask
  the user where it belongs rather than inventing a catch-all section.
- Propose the section names and the note-to-section assignment for approval
  in Step 7. The user decides whether the meeting is sectioned at all.

Quote rule (only when a transcript was provided):
- Quote only words that appear verbatim in the transcript. Never quote from
  the raw notes, from an interview answer, or from memory, and never
  reconstruct what someone probably said.
- Use two forms, chosen by significance:
  - Inline quote: a short quoted fragment inside the note's own sentence, in
    quotation marks with the speaker named, for wording that matters in
    itself (a specific commitment, a number, a term the group adopted).
  - Pull quote: a blockquote for an impactful statement, meaning one that
    decided something, committed someone, reversed a position, registered a
    real disagreement, or changed the meeting's direction.
- Format a pull quote as `> "<exact words>" — <Speaker>` on its own line
  directly under the note it supports, indented to that note's bullet.
- Include at most one pull quote per section, or one for the meeting when the
  notes are not sectioned. Skip any quote that only restates its note in
  other words: the bar is that a reader would want the speaker's own words.
- Trim with an ellipsis to cut filler or a false start. Never change,
  reorder, or clean up the words themselves.
- Attribute using the attendee names from Step 3, applying the same
  full-name-then-first-name rule. If the transcript labels speakers
  generically (for example `Speaker 2`) or names someone the attendee list
  does not include, ask the user who spoke rather than guessing.
- Propose every quote for approval in Step 7 alongside the note it attaches
  to. Where the transcript conflicts with the user's notes, ask; the user's
  notes stand unless the user says otherwise.

Image rule:
- For each screenshot/photo, ask the user for a caption describing its significance.
- Add the caption under each image using italic text (e.g., `*Caption describing the image*`).
- Give every image descriptive alt text in the Markdown itself
  (`![<alt text>](<path>)`), stating what the image shows.
- Interlace images with the notes using both signals: the image's content
  (what it shows, and which note that matches) and its timestamp (from the
  file name or EXIF data), which fixes where in the meeting it belongs.
- Keep images in chronological order by timestamp. When content and timestamp
  disagree about placement, follow the content and ask the user to confirm.
- When the notes are sectioned, place each image in the section its content
  belongs to, keeping chronological order within that section.
- If an image has no recoverable timestamp, ask the user where it belongs
  rather than guessing a position.

### Step 6: Format Notes as Bulleted List

After the interview and normalization, format the notes section as a bulleted list:
- Each note is a bullet point (`- `) containing a complete sentence.
- When the Step 5 topic rule produced sections, precede each section's
  bullets with its topic name as a bold line (`**Topic Name**`), separated
  from the previous section by one blank line. Do not use headings for
  topics: the Notes section is already an H6, and headings cannot nest below
  it.
- When no sections were identified, output a single flat bulleted list.
- Images should be interlaced at the appropriate position among the bullets based on their chronological timestamp and contextual relevance.
- Pull quotes sit directly under the note they support, inside that note's
  section.

### Step 7: Staged Approval Workflow

1. Propose updates to:
   - Meeting Metadata
   - Attendees
   - Notes, including any topic sections, transcript quotes, and image
     placement
   - The summary, when the Step 8 length rule applies
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
- Then the summary, when the length rule below applies
- Then `###### Attendees`
- Then `###### Notes`
- Then `###### Action Items`

Summary rule (based on read length):
- Measure the approved Notes section by its text alone: count the words and
  lines of the notes, captions, and quotes. Images do not count toward the
  measurement, so a short meeting does not earn a summary by carrying
  screenshots.
- Add a concise italicized summary when either trigger fires:
  - The Notes section exceeds ~500 words or ~40 lines. These are the same
    thresholds this project uses to decide when a documentation section is
    too long to read in place.
  - The notes are divided into three or more topic sections, however short
    they are. A reader scanning several sections benefits from knowing the
    shape of the meeting before reading it.
- When neither trigger fires, add no summary.
- Place it directly under the metadata line, and under the schedule note when
  one exists, before `###### Attendees`.
- Scale the summary to the read length:
  - Under ~500 words, where the section count is what triggered the summary:
    one to two sentences.
  - ~500 to ~1000 words, or ~40 to ~80 lines: two to three sentences.
  - Over ~1000 words or ~80 lines: up to five sentences, or one short bullet
    per topic section.
- The summary may only restate what the notes already say. It must not add
  facts, draw a conclusion the meeting did not reach, or list action items.
- Report the measurement (the word and line count, and the section count when
  the notes are sectioned) when proposing the document in Step 7, so the user
  can see why a summary was or was not added.

At the very end, append:
- `#### YYYY-MM-DD HH:MM: <Meeting Title>`
- Use 24-hour time.

## Quality Rules

- Keep output concise and readable.
- Quote only from a transcript the user actually provided, verbatim and
  attributed. Never invent, reconstruct, or paraphrase into a quotation.
- Add a summary only when the length rule calls for one, and section the
  notes only when the meeting genuinely had distinct topics. Neither is
  padding to apply by default.
- Preserve factual accuracy; do not invent details.
- Ask clarifying questions when uncertain.
- Follow requested section order and formatting exactly.
- Enrichment content must trace to a real source that was actually
  consulted (or material the user pasted). When no context sources are
  available, proceed with the user's notes alone; never simulate a source
  check or fabricate agenda, chat, email, link, or work item detail.
