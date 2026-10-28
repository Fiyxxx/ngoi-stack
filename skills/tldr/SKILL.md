---
name: tldr
description: Catch the user up on what happened in this session, short and plain, with what's verified and what needs them. Use when the user types /tldr, asks for a summary, recap or catch-up, or asks what's next, what the next steps are or where things stand.
---

# TLDR

Assume the user remembers what they asked and nothing after it. Tell them where things stand, not the story of how you got there.

## Before writing

- Re-read the user's messages. They decide what matters.
- Check the real state instead of recalling it: `git status`, the commits made this session, the diff, PR state with `gh`, ticks and Log in `.ngoi/specs/`. When your memory and the state disagree, the state wins.
- Agent reports and your own earlier messages are claims. A thing is verified only if a command, test or evidence file showed it this session.

## Shape

First line: the bottom line. What's waiting on the user, or "Nothing needs you."

Then only the sections that have something in them:

- **Done:** outcomes the user would notice, one line each, tagged `[verified: how]`, `[inferred]` or `[not checked]`.
- **Changed:** what is now different on disk or outside it: files, branches, commits, PRs, installs, settings.
- **Decided:** each decision, who made it (user or agent) and one line of why.
- **Needs you:** each question or call, with your recommendation.
- **Left:** what isn't done, failed or was dropped, and why.

End with one line of refs (paths, branches, hashes, PR links), only those needed to act.

## Rules

- About 150 words for a normal session, about 30 per item. Cut wording, never an item the user must act on.
- Outcomes, not actions: "Expired codes are rejected [verified: curl returned 400]", not "Updated validate()".
- Each line stays true when read alone.
- No numbers you didn't check. No items made up to fill a section.
- Leave out cosmetic changes, your reasoning, and dead ends, unless a dead end changed a decision.
- Plain words, per the wording list in `ngoi:unslop`.
- For a long or compacted session, work from the user's messages and the real state, not a replay of the transcript.
