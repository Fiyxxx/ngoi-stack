---
name: review
description: Independent, evidence-based review of a change. A verifier uses the real app like a user, and the same review runs on several models. Called by ngoi build after each unit. Also use when the user asks to review code, a branch, a PR or PR comments.
---

# Review

Prove the change works and is clean. Don't trust the author, including summaries, commit messages and PR text. Reviewers get the spec, the diff and the evidence, never the author's reasoning.

## Scope

- **From build:** the unit's diff (`git diff <base>...HEAD` plus the working tree), the spec and its done checks.
- **When the user asks:** whatever they point at. Without a spec, write a one-paragraph intent from the request, the commits and the code, and use it in place of done checks.
- **PR comments:** sort each one into fix, dismiss with a reason, or ask the user, using the same rules as the findings below.

## Tier

State the tier in one line before starting. The user can override it.

- **Quick:** no new behaviour, a small fix, a rebase, wording or style. Runs `.ngoi/check`, the verifier on only the done checks the change touches, and one `ngoi:reviewer` on sonnet.
- **Full:** new behaviour, a redesign, a large diff, the end of a unit, or the final gate. Runs everything below.

## Full round

1. **Gate.** Run `.ngoi/check`. If it's red beyond the recorded baseline, send the change straight back to the implementer and don't start reviewers yet.
2. **Start in parallel, in the background:**
   - One `ngoi:verifier` with the spec path, done checks, review focus, base and head commits, and `.ngoi/verify.md`.
   - Three `ngoi:reviewer` agents with the same prompt, on models opus, sonnet and haiku: the spec path, the diff command and the intent. The diversity comes from the models, not from personas.
3. **Merge the findings.** For each, note which models raised it and what the verifier showed. Two or more models finding it independently is the strongest signal. One model alone gets less weight.
4. **Judge as the lead reviewer:** a pragmatic senior engineer, not a vote counter. Put every finding in one bucket with a one-line reason:
   - **Act on.** Blocks. Only when it is (a) reproduced by a failing test, a command or verifier evidence, or (b) a concrete violation of a spec line or a principle at a named place in the diff, such as a one-caller wrapper, an unused export, or a guard for a state that can't happen.
   - **Consider.** Plausible but unproven, or not worth the cost now.
   - **Noted.** True, but no action needed.
   - **Dismissed.** Wrong or out of scope, with the reason.

   A problem outside the done checks and review focus becomes a question for the user ("should the spec cover this?"), never a patch.

## Loop

Send Act-on findings to a fresh `ngoi:implementer` with the finding, its evidence and these rules:

- Fix causes, not instances. Several findings with one cause get one fix at the cause.
- A guard is a fix only when the state it guards can really happen.
- The implementer may reject a finding with evidence. You judge.
- If two fixes resting on the same assumption fail the same check, stop patching and test the assumption.

Re-review the fix at the Quick tier. Fully re-check the items that failed, plus the passed checks whose files the fix touched. Compare the diff size before and after each fix round; added lines need a reason. Round 3 is the last: one fix, one re-check, then list what's left for the user.

## Output

Short:

- verdict: clean, clean with notes, or not clean;
- the evidence table;
- Act on, Consider, Noted and Dismissed, with the models and reasons;
- what changed during review and why;
- decisions for the user.
