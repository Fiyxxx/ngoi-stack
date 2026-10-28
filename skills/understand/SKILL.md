---
name: understand
description: Explain why something was decided or how part of the system works, grounded in the code and its history. Use whenever the user asks why or how about the codebase, a design decision, a spec, a diff, or what an agent did.
---

# Understand

Answer the question the user asked, at the depth they asked. Read-only.

- **How:** trace the real path from entry point through each layer to the data, citing file:line at every step. Use Explore subagents for wide reads.
- **Why:** look for the reason in the spec (`.ngoi/specs/`, its Decisions and Log), commit messages, PRs (`gh`), `git blame` on the lines, and comments. Say where the reason came from. If no source states it, say so and give your inference, labelled as inference.
- **A change:** tell it in the order a reader needs, usually the new data shape first and then who uses it, not file order. Include what was tried and dropped if the spec's Log records it.
- **A diagram** only when the structure is easier to see than read.

Every claim cites file:line, a commit or a spec line. Label anything you didn't verify as inferred. Keep it short. If the explanation exposes a problem, say so plainly.
