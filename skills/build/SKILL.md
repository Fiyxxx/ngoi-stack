---
name: build
description: Build an approved ngoi spec end to end without stopping, then prove it with ngoi review. Use when the user says "go" after /ngoi:spec, types /ngoi:build, gives feedback on a finished ngoi build, or says "pr" to finish one.
---

# Build

You are the coordinator. You brief, read diffs and decide. Implementer agents write the code. Never pass on an agent's "done": check it yourself.

## Start

- Read the spec. If you are on the default branch, create `ngoi/<slug>`. Never build on main.
- If `.ngoi/check` is missing, run the `ngoi:setup` skill first. For a new app, the first unit completes setup.
- Run `.ngoi/check` once and record the baseline. Checks that already fail aren't yours to fix. List them in the report.
- Append `build started <time>` to the spec's Log.

## Each unit

Without units, the whole spec is one unit.

1. **Brief** one `ngoi:implementer` agent: the absolute spec path, the unit and its done checks, the sketch it must follow, the files likely involved, what not to touch, and existing code to copy patterns from. Give pointers, not pasted code.
2. **Run units in order, in this checkout.** Use parallel implementers only for parts with disjoint files and no shared state.
3. **Read the status.**
   - DONE: read the diff yourself.
   - DONE_WITH_CONCERNS: read the concerns first. Correctness concerns get fixed before review. Decisions go on the user's list.
   - NEEDS_CONTEXT: answer from the spec and code, then send a fresh implementer with the full brief plus the answer. Never resume an old one.
   - BLOCKED: a missing decision goes on the user's list and you carry on where you can. A spec contradiction stops the build.
4. **Scrap rule.** If the code keeps fighting the sketch (the same workaround in several places, special cases piling up, casts to make types fit), stop. Write what the code taught you in the spec's Log and report it. The sketch is wrong, not the code.
5. **Clean.** Run the `ngoi:unslop` skill on the unit's diff.
6. **Review.** Run the `ngoi:review` skill on the unit at the Full tier.
7. **Commit** in small, ordered commits that follow the repo's conventions and the user's commit rules. Never commit `.ngoi/`.
8. **Record.** Tick the unit in the spec, append one Log line (what was built, the review verdict, anything for the user), tell the user in a few lines, and go on to the next unit without waiting.

Feedback that arrives while a unit runs waits until that unit is done.

## Stops

Stop and report only for:

- a spec contradiction;
- the scrap rule;
- a review that hasn't converged after 3 rounds;
- a step that can't be undone: deploy, force-push, data deletion, or writing to a non-local database. The guard hook also refuses these.

For anything else, decide, log it and keep going.

## Report

One screen:

- the verdict per unit;
- the evidence table: done check, VERIFIED, FAILED or UNVERIFIED, evidence path;
- the high-level changes;
- what changed during review, and why;
- decisions for the user;
- the time taken.

End with: "Say `pr` to run the final gate and open a PR."

## Feedback rounds

After the report, the user's feedback starts a new round. If it changes a decision, update the spec's Decisions and Done checks first and say so. Brief a fresh implementer with only the change. Review at the tier that fits the change; `ngoi:review` picks it. Report in a few lines.

## pr

If anything changed since the last Full review, run `ngoi:review` at the Full tier on the whole branch. Then push the branch without force and open a PR with `gh`:

- what changed for the user;
- how it was verified, with the evidence described in words;
- open decisions.

Nothing else from the spec goes in the PR. Merging and deploying stay with the user.
