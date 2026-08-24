# Style card mechanics

Reference for the `writing` skill, Step 6: how a card's counts are read when it
has a ledger behind it, and the ledger format itself. SKILL.md carries the
decisions a run needs on every request; this file carries the parts consulted
only when a card actually has two horizons to reconcile, which fresh research
never does.

## Counts carry two horizons

**Every counted line carries three things**, and a line missing any of them has
dropped back to the impression this skill exists to replace:

1. The **observation** itself.
2. A **count**, always. `"Jordan," capitalized` with no figure behind it is not
   a finding, and a line that loses its count has almost always lost it while
   being reformatted rather than for want of evidence.
3. **Both figures whenever the horizons differ**, the recent one and the
   all-time one. A single figure is right only when the two agree and collapse
   (rule 3 under *Which figure the draft is written to*), or when there is nothing recent to report (rule 2).

The wording is free. `8 of 8 recent | 22 of 24 all time` and a second line
reading `was "hey Jordan," lowercase   6 of 6 (2023)` say the same thing, and
either is fine. What is not free is dropping the older figure once the horizons
disagree: the disagreement is the finding, and a line showing only the recent
count has quietly discarded the evidence that made it worth raising.

Recent is the last twelve months, and the card prints the span it actually
covers. How many samples land in that window decides what happens next:

| Samples in the last 12 months | What the card does |
|---|---|
| 3 or more | Split the counts. The recent figure is the reading. |
| 1 or 2 | Do not split. Use the all-time figure, and say recent coverage is thin, naming the count. |
| None | Do not split. Use the all-time figure, say the recent window is empty, and **cap confidence at medium**, or at low if it was already medium. |

Do not widen the window to manufacture a recent reading. A correspondent
written to twice a year genuinely offers no basis for separating current style
from overall style, and `4 of 4 (2023-11 -> 2026-08)` with a note that nothing
is recent is the honest card. Stretching the window until three samples fall
inside it would report a 2023 habit as current.

Re-bucketing happens on read, by comparing the ledger's dates against today.
It is counting, not searching, and it costs nothing.

**Count into buckets. Never decay-weight.** A weighted "4.7 of 6.2" cannot be
checked by the user reading the card, cannot be edited by hand, and fails the
standard that every claim trace to a count.

Which figure the draft is written to:

1. **Recent meets the threshold.** It wins outright, and the all-time figure is
   context rather than input.
2. **Recent is empty.** Fall back to all time, and lower the confidence: cap
   it at medium, or at low if it was already medium. Naming the empty window
   while leaving `Confidence: high` in place is not lowering it -- the reading
   is high-quality evidence about a period that has ended, which is a weaker
   claim about today than the same counts drawn from current mail.
   *No recent samples* and *habit abandoned* are different facts. Not having
   written to someone in eighteen months tells you nothing about how they would
   be written to today, and reporting that as a changed habit invents a finding.
3. **Both have evidence and they agree.** Collapse to one figure:
   `no em dashes (0 of 24, since 2023-04)`. Most lines collapse, which is why a
   slow-moving trait like punctuation costs nothing to carry for years.
4. **Both have evidence and they disagree.** That is a finding, not
   bookkeeping. Print both and raise it when the card is shown: "you used to
   say ticket, the last eight say issue, which is current?" A card kept for
   years is the only thing that can see a change like this, and the user is the
   only one who can settle it.

## The ledger

A stored card carries the samples its counts came from, so a later session can
extend it without re-reading the corpus. Re-bucketing then happens on read, by
comparing the ledger's dates against today -- counting, not searching.

The format, and the rules about what may go in it, are in
[cache-files.md](cache-files.md), which documents every file in the cache. It is
deliberately not repeated here: two copies of a format drift apart, and the copy
you happen to be reading is always the stale one.

## Vocabulary slots

**Vocabulary.** Record this in slots rather than as a list of words. Fixing the
slots is what makes the reading specific without making it long: the ceiling is
set by the slot count rather than by however much the corpus happens to hold,
and an empty slot is itself a finding. The slots deliberately do not overlap
`Opening`, `Closing`, `Mechanics`, or `Emoji`, which already cover greetings,
sign-offs, punctuation, and emoji.

| Slot | What goes in it |
|---|---|
| `marker` | discourse markers and connectives: "so", "anyway", "that said", "heads up" |
| `hedge` | hedges and boosters: "I think", "pretty", "definitely", "kind of" |
| `stance` | how good and bad get named: "solid", "rough", "fine" |
| `term` | naming choices for recurring referents: ticket vs issue vs card |
| `shorthand` | domain jargon and abbreviations, and whether they get expanded |
| `filler` | filler and profanity |
| `avoid` | words absent from the corpus, especially assistant escalations |

## Polish tiers

**Polish tier**, on this ladder:

| Tier | Markers |
|---|---|
| **1 — Fire-off** | One or two lines, no greeting or sign-off, lowercase, fragments, abbreviations, typos left alone |
| **2 — Quick note** | First-name greeting or none, contractions, one to three short paragraphs, minimal formatting, one clear ask |
| **3 — Considered** | Greeting and sign-off, complete sentences, deliberate structure, explicit ask and context, proofread |
| **4 — Formal / public** | Full structure, careful diction, no slang, edited for a reader who may quote it |

The tier comes from the samples, not from the topic's importance. Where the
current situation differs from every sample (bad news to someone the user only
ever jokes with, a first message to a new client), say so and confirm the tier
before drafting.
