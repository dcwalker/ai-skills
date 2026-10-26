# Email Sift Rubric

Sift labels new Gmail by importance on a schedule, and reads this doc in full
before every run. It's my definition of what matters, and a living document:
sift keeps every section current as it learns how I handle mail, marks what
it inferred, and records each change in the Changelog. Keep it under about
two pages.

Timezone: UTC (change to yours, such as Europe/Berlin)

## How to use this doc

- **Change a rule:** edit any section. Sift follows it from the next run and
  keeps the rest of the doc consistent with it.
- **Correct sift:** add or edit a rule here; the next run follows it. Fixing
  one thread's label or Important mark in Gmail fixes that thread only, and
  sift won't undo it.
- **Let sift learn on its own:** once a day, sift checks how I handled the
  mail it labeled. When I reply to or star several threads from one sender
  that it ranked low, or archive its Important mail unread, it adds or
  rewrites the rule in the section it belongs to, starting with "(observed)".
- **Check sift's close calls:** when this doc doesn't settle a kind of mail,
  sift makes the call and writes it as a rule starting with "(inferred)" in
  the section for that priority. Edit the line to change the call, or remove
  "(inferred)" to make it yours. Sift doesn't ask questions or read comments.
- **Choose newsletters:** list the ones I want to read under Newsletters,
  Valued. Every other newsletter gets AI/Bulk. Sift adds lines there too, each
  starting with "(learned)", from its daily check.
- **Choose tabs:** say under Tabs which mail goes in Social, Promotions, or
  Updates. Sift moves mail to match, whatever tab Gmail picked, and keeps a
  tab I set by hand.
- **Allow more than labels:** add it under Permissions, for example
  "Archive threads labeled AI/Junk". Only I add permissions or notifications.
- **Tell sift about yourself:** add notes under About me, grouped by topic.
  Sift adds its own notes there too, each starting with "(inferred)". Edit one
  to correct it, or remove "(inferred)" to make it yours.

## Labels

Every label and mark sift applies, and when. A thread gets one priority, plus
a star and category labels when they fit, each judged on what the message is,
not on the words it uses. Sift creates labels under AI/ and keeps this table
current, adding a row for each label it starts using.

| Label | When sift applies it |
|---|---|
| Important (Gmail's mark) | Priority: I'd want to see it today |
| AI/Low priority | Priority: meant for me, nothing urgent |
| AI/Bulk | Priority: mass mail I wouldn't miss if it were archived unread |
| AI/Junk | Priority: mail I never want |
| Star | Someone is waiting on me (see Needs reply) |
| AI/Receipt, AI/Statement, AI/Invoice | The message is one, or carries one as an attachment. One that only talks about one ("where is my receipt?") gets none |
| AI/Newsletter | It works as a newsletter, whatever it calls itself: a "newsletter", a "gazette", or a regular Friday update that reads like one |
| AI/Travel | Booking confirmations, itineraries, boarding passes, and check-in reminders for trips I've booked; not travel deals |
| AI/Delivery | Tracking, "out for delivery", and "delivered" notices for orders I've placed; not shipping promotions |
| AI/Appointment | Confirmations, reminders, and reschedules for appointments I have; not "book your next visit" promotions |
| AI/Security | Sign-in alerts, password resets, and verification codes from services I use; a lookalike sender is Junk instead |

## About me

Who I am, the people in my mail, and what matters to me right now, grouped by
topic so related notes sit together. Sift reads this before every run and
keeps it current: it adds lines that start with "(inferred)", with where it
learned each one and when, corrects lines when it learns better, and moves
notes so related ones sit together.

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

Mail meant for me that doesn't meet the rules above, even from a no-reply
sender, including:

- Automated notifications that only confirm something already done
- Group threads where I am Cc'd and nothing is asked of me
- Newsletters on my Valued list
- Receipts and statements
- FYIs from people I know
- Review requests and order follow-ups from companies I've actually bought
  from, even when they read like marketing

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

## When torn

When a message could fit two priorities, choose the less severe:

- Important over Low priority: a false alarm costs a glance, while a miss may
  never be noticed
- Low priority over Bulk: mail meant for me belongs in Low priority
- Bulk over Junk: mass mail I signed up for belongs in Bulk
- Low priority over Junk: dull legitimate mail is never Junk

## Tabs

Every Gmail inbox tab and how I want it used, whatever tab Gmail chose. Sift
files every thread it labels by this table, judged on what the message is,
apart from its priority, and adds a row for any tab Gmail adds, unused until I
say what goes there.

| Tab | What goes here | Related labels |
|---|---|---|
| Primary | Important mail, and anything the other rows don't place | Important, AI/Low priority |
| Social | Notifications from social networks and fitness or community apps | Usually AI/Bulk |
| Promotions | Marketing, sales, and newsletters from stores and brands | AI/Bulk, AI/Junk, AI/Newsletter |
| Updates | Receipts, statements, invoices, and bills; delivery, travel, and appointment notices; account and security alerts; automated notifications that only confirm something already done | AI/Receipt, AI/Statement, AI/Invoice, AI/Delivery, AI/Travel, AI/Appointment, AI/Security |
| Forums | Nothing: I don't use this tab | |

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
