# Email Sift Rubric

Sift labels new Gmail by importance on a schedule, and reads this doc in full
before every run. It's my definition of what matters. Every rule above "Added
by sift" is mine, and sift never changes those. Keep it under about two pages.

Timezone: UTC (change to yours, such as Europe/Berlin)

## How to use this doc

- **Change a rule:** edit any section above "Added by sift". Sift never changes those.
- **Correct sift:** add or edit a rule here; the next run follows it. Fixing
  one thread's label or Important mark in Gmail fixes that thread only, and
  sift won't undo it.
- **Let sift learn on its own:** once a day, sift checks how I handled the
  mail it labeled. When I reply to or star several threads from one sender
  that it ranked low, or archive its Important mail unread, it adds a rule
  starting with "(observed)" under Added by sift.
- **Answer a question:** sift asks in comments that start with "Sift:". Reply
  in the thread, and the next run applies your answer.
- **Choose newsletters:** list the ones I want to read under Newsletters,
  Valued. Every other newsletter gets AI/Bulk. Sift adds lines there too, each
  starting with "(learned)", from its daily check.
- **Allow more than labels:** add it under Permissions, for example
  "Archive threads labeled AI/Junk".
- **Tell sift about yourself:** add notes under About me, grouped by topic.
  Sift adds its own notes there too, each starting with "(inferred)". Edit one
  to correct it, or remove "(inferred)" to make it yours.

## Labels

| Label | Meaning |
|---|---|
| Important (Gmail's mark) | I'd want to see it today |
| AI/Low priority | Meant for me, nothing urgent |
| AI/Bulk | Mass mail I wouldn't miss if it were archived unread |
| AI/Junk | Mail I never want |
| Star | Someone is waiting on me |

## About me

Who I am, the people in my mail, and what matters to me right now, grouped by
topic so related notes sit together. Sift reads this before every run. Lines
I write are mine. Sift adds lines that start with "(inferred)", with where it
learned each one and when, and it edits only those lines. To keep related notes
together, sift may move any line here, mine included, but never changes my
words.

### (topic, such as Kids' soccer, Home, or Work)

- (I add these)

## Always important

Senders, topics, or situations that should always be marked Important.

- Anything from a person I have written to in the last 90 days, unless it is clearly bulk mail
- Deadlines, payments, or schedule changes affecting the next 7 days

## Needs reply

What counts as someone waiting on me specifically, which sift stars. It
depends on the message, not on who sent it.

- A direct question addressed to me by name or as the only recipient
- Requests for a decision, approval, or volunteer sign-up
- A statement addressed to me that needs me to acknowledge it, such as a
  confirmation someone is waiting on

Not a reply, even from someone I know:

- A message to a group that only shares information, such as a note to all
  tenants about a visit
- An acknowledgment of my own message, such as "ok, thanks" or "got it"

## Low priority

Mail meant for me that doesn't meet the rules above, including:

- Automated notifications that only confirm something already done
- Group threads where I am Cc'd and nothing is asked of me
- Newsletters on my Valued list
- Receipts and statements
- FYIs from people I know

## Bulk

Mass mail I wouldn't miss if it were archived unread, including:

- Newsletters not on my Valued list
- Promotions from companies I've signed up with or bought from
- Social network notifications

## Newsletters

Valued newsletters get AI/Low priority. Every other newsletter, listed under
Not valued or not listed at all, gets AI/Bulk. One per line: name | sender.

### Valued

- (I add these)

### Not valued

- (I add these)

## Junk

Mail I never want, including:

- Promotions and marketing I didn't ask for, even when worded urgently
- Spam-like or phishing-like messages

## Category labels

Labels sift adds alongside the priority label, judged on what a message is,
not on the words it happens to use. Sift creates each one under AI/.

- **Receipts, statements, and invoices:** label a message AI/Receipt,
  AI/Statement, or AI/Invoice when it is one, or carries one as an attachment.
  A message that only talks about one, such as "where is my receipt for
  Thursday?" or "I never got an invoice in the mail", gets none of these
  labels.
- **Newsletters:** label a message AI/Newsletter when it works as a newsletter,
  whatever it calls itself: a "newsletter", a "gazette", or a regular Friday
  update that reads like one.
- **Travel:** label AI/Travel the booking confirmations, itineraries, boarding
  passes, and check-in reminders for trips I've booked. Travel deals and
  "where to next?" marketing don't count.
- **Deliveries:** label AI/Delivery the tracking updates, "out for delivery",
  and "delivered" notices for orders I've placed. Shipping promotions don't
  count.
- **Appointments:** label AI/Appointment the confirmations, reminders, and
  reschedules for appointments I have, such as a doctor, dentist, or car
  service. "Book your next visit" promotions don't count.
- **Account security:** label AI/Security the sign-in alerts, password resets,
  and verification codes from services I use. A message that only looks like
  one, from a lookalike sender, is Junk instead.

## Added by sift

Rules sift learned from my answers to its questions, and "(observed)" rules
from its daily check of how I handle mail. Sift adds, sharpens, and
consolidates rules only here. A rule here can narrow one of mine for the
cases it names.

- (sift adds these)

## Permissions

Actions beyond priority labels that sift may take, by category. Empty means
priority labels only. For example: "Archive threads labeled AI/Junk", or
"Label event invitations as invitation". Sift creates any label I name here
under AI/ in title case (AI/Invitation).

- (none yet)

## Notify

Mail that should send me a push notification when sift labels it. Empty means
sift never notifies me; its runs report only in the log.

- (none yet)

## Examples

Real cases that teach the rules. Format: sender | subject | correct label | why.

- (sift adds these)

## Changelog

Newest first. Date | change | prompted by.

- (sift adds these)
