# Processing Order

Step 1b in full: which order to work a set of items in, where each platform
keeps that order, and what to ask when nothing settles it. Read this before
stating an order on the `Order:` line. A scope of one item has no order to set
and skips all of it.

## Why the order matters

The order the user keeps their items in is information. A Trello list sorted
top to bottom, a Jira backlog ranked by hand, or an inbox read oldest first all
say what the user means to deal with first. Presenting the items one at a time in
that order keeps the triage in step with how the user
already thinks about the work. Working it in whatever order a tool happened to
return throws that away.

## The signals, in order

Take the first that applies, and record which one it was:

1. **An order the user stated.** "Do the overdue ones first", "go by due date",
   "start with the school emails". This always wins.
2. **The user's preferences file**, when it names an order for this kind of
   scope ("Inbox: Starred first, then oldest first").
3. **The source's own order**, on the platform the user asked to triage. See
   the platform notes below. Only the triaged platform's order counts: when
   triaging a Trello list turns up a linked Jira issue, the issue is worked
   where its card sits in the list, not where it sits in the Jira backlog, and
   the reverse when triaging Jira.
4. **A ranking or importance signal**: a priority field, an urgent or flagged
   label, Gmail's Starred or Important, a due date. These apply when the source
   has no order of its own, as in an inbox.
5. **Chronological, oldest first.** First in, first out: the item that has
   waited longest is worked first.

## Platform notes

**Trello.** A list's order is its cards top to bottom. `view_list` returns the
cards in that order, and it does not print their positions, so the order is
the order of the listing itself. A board's order is its lists as `view_board`
returns them, then each list's cards top to bottom. Due dates, labels, and
creation dates on the cards do not override this; the user arranged the list.

**Jira.** When the user shared a JQL query or a saved filter that carries its
own `ORDER BY`, that is the order: run the query as given. Otherwise the order
is rank, the backlog order a team sets by dragging issues: search with
`ORDER BY Rank ASC` appended to the query, and take the results in the order
returned. Rank is not printed in the results; the order of the results is the
rank. Priority and due date do not override rank either.

**Gmail.** An inbox has no order of its own, so it goes by signals 4 and 5
without asking, unless the preferences file says otherwise: threads carrying
`STARRED` or `IMPORTANT` in their `labelIds` first, then the rest, each part
oldest first. `search_threads` lists the newest thread first, so this usually
means reading the listing from the bottom up. A Gmail label or search query is
treated the same way.

## When to ask

Chronological always applies, so the question is never whether some order
exists but whether the signals agree.

**Two sources, two orders: ask first.** When the scope spans sources with no
shared order (two platforms, two boards, or two projects, each with its own
order), ask once before any item is worked, name the orders that would make
sense, and process nothing until the user answers. Changes authorized up
front do not answer this question:

> "This covers your Errands list in Trello and the OPS Jira project, and they
> each keep their own order. Which should I go by?
> 1. The Trello list first, top to bottom, then the OPS backlog by rank
> 2. Everything by due date, soonest first, undated items last
> 3. Everything oldest first"

**One source, conflicting signals: pick, say so, and offer to switch.** When
two signals on the same level disagree inside one source, such as a
high-priority item due after a low-priority one with nothing above them to
settle it, take the earlier-listed signal (priority before due date), name
the conflict on the `Order:` line, and say the user can switch at any time,
as a statement rather than the reply's one question. Changes
authorized up front go ahead in the chosen order meanwhile.

## Groups do not change the order

Groups of similar items (by sender, label, list, and so on), whether a batch
the user directed or a decision offered for similar items, never reorder the
items: everything still in scope is worked in the order above. In an inbox going oldest
first, a bank's newest promotion is not pulled forward because the bank's
oldest thread comes first.

## No numbering

Items are not numbered. Each reply presents one item, named by its linked or
quoted title, so a position number adds nothing the user can use, and read
aloud it is noise. Urgency never moves an item forward: an urgent item is
flagged with `⚠️` on its own summary line when its turn comes.

## Recording it

State the order and the signal it came from on the Scope Confirmation block's
`Order:` line, so the user can correct it before anything is applied:

```
Order:     list position, top to bottom (Trello list order)
Order:     rank (OPS backlog, ORDER BY Rank ASC)
Order:     due date, soonest first (your ORDER BY duedate)
Order:     Starred or Important first, then oldest first (inbox default)
Order:     single item
Order:     asked (scope spans Trello and Jira)
```

The block, with this line, is shown once, in the first item's reply, and
again only if the scope or the order changes.
