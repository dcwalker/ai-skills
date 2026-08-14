# The queue that ate a weekend

We lost a weekend to a retry loop that any of us could have found in ten
minutes, if any of us had been looking for it. I want to write down how that
happened, because the bug is boring and the reason we missed it is not.

The export queue retries failed jobs. Sensible. It retries them without a
cap, which is less sensible, and it does that only when the failure comes
back as a timeout rather than an error. So the loop needs two conditions to
fire, and neither one is visible in the code that looks like it owns the
behaviour.

Here is the part I keep chewing on. We had a dashboard for queue depth. We
had alerts on error rate. We had nothing at all on the same job appearing
four times, because nobody had imagined that shape of failure, and a
dashboard only shows you the failures you already thought of.

I do not have a tidy conclusion. We capped the retries. We added a metric on
duplicate job ids. Neither of those would have helped with the next thing,
which will also be a shape nobody imagined.
