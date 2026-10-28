---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
---

# Systematic debugging

Adapted from superpowers' systematic-debugging (MIT, Jesse Vincent).

**Core principle:** find the root cause before attempting any fix. A fix for a symptom is a failure.

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

Use it for any technical issue: test failures, production bugs, unexpected behaviour, build failures, integration problems. Use it **especially** under time pressure, when a quick fix seems obvious, or after a fix already failed. Simple bugs have root causes too.

## Phase 1: Root cause investigation

Before any fix:

1. **Read the error completely.** The stack trace, line numbers, file paths and codes often contain the answer.
2. **Reproduce it reliably.** What are the exact steps? Does it happen every time? If you can't reproduce it, gather more data. Don't guess.
3. **Check recent changes.** `git log`, the diff, new dependencies, config, environment.
4. **Find where it breaks across components.** In a system with several parts (API, service, database), log what goes into and out of each boundary once, find the layer where good data turns bad, then investigate that layer.
5. **Trace the data backwards.** Where did the bad value come from? Who called this with it? Keep going up until you reach the source, and fix it there, not where the error appears.

### Bugs that depend on real data

"Wrong for some users" usually lives in the data. Agents never query a non-local database (the ngoi guard refuses it). Instead:

1. Write the exact **read-only** query that would show the bad case.
2. Ask the user to run it themselves with the `!` prefix, and work from their output.
3. Reproduce locally by building a small fixture from that output, with personal data replaced. Never write to production.

## Phase 2: Pattern analysis

1. Find similar code in the repo that works.
2. If you're following a reference implementation, read all of it. Don't skim.
3. List every difference between the working and broken cases, however small.
4. Name the dependencies, config and assumptions the broken path relies on.

## Phase 3: Hypothesis and test

1. State one hypothesis: "X is the root cause because Y."
2. Test it with the smallest possible change, one variable at a time.
3. If it's confirmed, go to Phase 4. If not, form a new hypothesis. Don't stack fixes.
4. If you don't understand something, say so and investigate further.

## Phase 4: Fix

1. **Write a failing test first** that reproduces the bug: an automated test, or a one-off script if there's no test framework.
2. **Show the user the root cause and the failing reproduction before fixing,** unless they already asked you to fix it. Small fixes go ahead with their OK. Larger ones go through `/ngoi:spec`.
3. **One fix, at the root cause.** No "while I'm here" changes and no bundled refactoring.
4. **Prove it.** The test passes, `.ngoi/check` is green, and the bug is gone on the real app. Run `ngoi:review` at the Quick tier when the repo has `.ngoi/verify.md`.
5. **If the fix fails,** go back to Phase 1 with what you learned. After 3 failed fixes, stop. Three failures mean the design or the assumption is wrong, not the fix. Write down the assumption the fixes shared, test it directly, and discuss it with the user before a fourth attempt.

## Red flags: stop and return to Phase 1

- "Quick fix for now, investigate later."
- "Just try changing X and see."
- Several changes at once, then running the tests.
- "It's probably X, let me fix that."
- Proposing fixes before tracing the data.
- "One more fix attempt" after two have failed.
- Each fix reveals a new problem somewhere else.

The user's signals that you're guessing: "Is that actually happening?", "Stop guessing", "Will it show us...?", "We're stuck?". When you see these, go back to Phase 1.

## Rationalisations

| Excuse | Reality |
|---|---|
| "Too simple to need the process" | Simple bugs have root causes. The process is fast for them. |
| "No time" | Systematic is faster than thrashing. |
| "I'll test after the fix works" | Untested fixes don't stick. The test proves the fix. |
| "Several fixes at once saves time" | You can't tell which one worked, and you add new bugs. |
| "I see the problem" | Seeing the symptom isn't understanding the cause. |

If the investigation shows the cause is genuinely external or timing-dependent, write down what you checked, handle it where it enters the system, and add logging so the next occurrence carries evidence. Most "no root cause" cases are incomplete investigations.
