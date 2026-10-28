# ngoi

**Not Gonna Overengineer It.** A small Claude Code plugin for one way of working: you approve a short spec once, agents build it without stopping, and an independent review proves the change on the real app before you see it.

It doesn't trust the AI. Nothing counts as done until a separate agent has used the app like a user and saved the evidence, and a hook refuses the usual shortcuts (suppressions, skipped tests, loosened config, force-pushes, deploys).

## The flow

```
/setup          once per repo
/spec <dump>    you push back until it's right, then say "go"
   go           every unit is built, cleaned and reviewed, no stops
   feedback     plain messages start a small round
   pr           final review of the branch, then a PR
```

You merge and deploy. ngoi never does either.

## Commands

The `ngoi:` prefix is optional while no other command has the same name. `/review` is Claude Code's built-in review, so type `/ngoi:review` for this one.

| Type | Or let it trigger | What you get |
|---|---|---|
| `/setup` | when build finds no setup | `.ngoi/check` and `.ngoi/verify.md`, proven on your app once |
| `/spec <dump>` | never, you type it | a short spec you approved, then the build starts |
| `/build` | on `go`, feedback, or `pr` | the code, reviewed and committed on an `ngoi/<slug>` branch |
| `/ngoi:review` | "review this branch / PR / comments" | an evidence table and findings sorted by what to do |
| `/understand` | any why or how question | an answer with file:line for every claim |
| `/unslop` | "clean this up" | AI tells removed from code, wording and UI |
| `/systematic-debugging` | any bug or failing test | the root cause, shown to you before the fix |
| `/tldr` | "catch me up", "what's next?" | where things stand in about 150 words |

## Skills

### setup

Prepares a repo once. It reads the repo first (scripts, CI, README, docker-compose) and asks only what it can't see.

- **`.ngoi/check`** runs typecheck, lint and tests, reusing what CI runs. Exit 0 means green.
- **`.ngoi/verify.md`** tells an agent how to launch the app on a free port with its own local database, drive it (browser, `curl` or CLI), capture evidence, clean up, and walk the 3 to 6 main user journeys.
- It proves the guide by launching the app and driving one journey. A guide nobody ran is a draft.
- `.ngoi/` goes in `.git/info/exclude`, so nothing ngoi writes reaches git.

### spec

Turns your rambling dump into a spec agents can build without guessing. It works for a one-line tweak and for a multi-unit feature.

1. **Grounds itself** in the code and earlier specs, and doesn't re-ask settled decisions.
2. **Plays it back in one message:** the goal, the size, the approach and units, the done checks with the evidence that will prove each one, and the open decisions with a recommendation. Decisions are marked as yours or the agent's guess. Where running something can answer a question, it prototypes instead of asking.
3. **Takes your pushback** and answers with file:line, not reassurance.
4. **Writes** `.ngoi/specs/YYYY-MM-DD-slug.md`: goal, not doing, decisions, done checks, a sketch of types and boundaries (no function bodies), review focus, units and a log. A tweak gets no file.
5. **Builder check:** a fresh agent reads the spec and lists every question it would need answered. Only the ones that change behaviour come to you.
6. **On "go"** it starts the build. You approve once, for every unit.

### build

Runs the approved spec to the end. The main session coordinates, and fresh agents write the code.

- Works on an `ngoi/<slug>` branch, never main, and records the baseline of checks that already fail.
- For each unit: brief an implementer, read the diff, run `unslop`, run a Full review, commit in small steps, tick the spec and move on.
- **Scrap rule:** if the code keeps fighting the sketch, it stops and says the sketch is wrong instead of piling up workarounds.
- Stops only for a spec contradiction, the scrap rule, a review that hasn't converged after 3 rounds, or something that can't be undone.
- Ends with a one-screen report: verdicts, an evidence table (VERIFIED, FAILED or UNVERIFIED per done check), what changed during review, and decisions for you.
- **Feedback** after the report starts a small round, with a review sized to the change.
- **`pr`** runs the final review on the whole branch, pushes without force and opens the PR with `gh`.

### review

Proves a change works and is clean. It never trusts the author's summary.

- **Quick tier** for small fixes and tweaks: the check script, the verifier on the affected done checks, and one reviewer.
- **Full tier** for new behaviour and the end of each unit: the check script, then a verifier and three reviewers (opus, sonnet, haiku, same prompt) in parallel.
- Findings agreed by several models count most. Each finding lands in one bucket: **Act on** (only if reproduced, or a concrete violation at a named place), **Consider**, **Noted** or **Dismissed**, each with a reason.
- Fixes go to a fresh implementer, which may push back with evidence. It fixes causes, not instances. The loop ends after 3 rounds and hands you what's left.
- Works on demand for any branch, PR or set of PR comments, with or without a spec.

### understand

Answers why and how questions about the code, a spec, a diff, or what an agent did. Read-only.

- **How:** traces the real path from entry point to data, with file:line at each step.
- **Why:** finds the reason in the spec, commits, PRs or `git blame`, and says where it came from. Guesses are labelled as inferred.

### unslop

Removes AI tells from the diff in three lists: code (`references/code.md`), wording (`references/wording.md`) and UI (`references/ui.md`). It keeps behaviour and meaning, never touches test assertions, and lets your design system win.

### systematic-debugging

Root cause before any fix. It reproduces, traces the bad value back to its source, tests one hypothesis at a time, and writes a failing test first. It shows you the cause before fixing. For bugs that depend on production data, it writes a read-only query for you to run with `!`, never touching that database itself. After 3 failed fixes it stops and questions the assumption.

### tldr

Catches you up on the session. The first line is what's waiting on you. Then Done, Changed, Decided, Needs you and Left, each only if it has something. Every outcome is tagged verified (and how), inferred or not checked. It checks git and the specs rather than trusting its own memory of the chat.

## Agents

| Agent | Model | Job |
|---|---|---|
| implementer | opus | Writes one unit or fix. Reports DONE, DONE_WITH_CONCERNS, BLOCKED or NEEDS_CONTEXT. |
| verifier | opus | Uses the app like a user to prove each done check, runs one regression journey on base and head, and adds missing tests. Writes only tests and evidence. |
| reviewer | opus, sonnet, haiku | Reads the diff against the spec for correctness, code that shouldn't exist, gaming, slop and security. Never edits. |

## Guard

`hooks/guard.py` runs before every edit and shell command, including under bypass permissions. It checks only what an edit adds, so removing a suppression always passes. It refuses:

- suppressions: `eslint-disable`, `@ts-ignore`, `# type: ignore`, `# noqa`, coverage exclusions, `as unknown as`, empty catch blocks;
- TBD, FIXME or XXX without a ticket reference;
- skipped or focused tests, and deleting test files;
- loosened lint, type or CI config;
- subagents editing `.ngoi/check` or `.ngoi/verify.md`, and the verifier writing anything but tests and evidence;
- force-push, deploy and publish commands, destructive SQL, and any non-local database.

Docs files and ngoi's own source are exempt.

## Principles

`principles.md` holds ten rules every agent follows, such as the smallest change, root causes, proving it on the real thing, and labelling claims. Symlink it as your global `CLAUDE.md` so every session gets them:

```sh
ln -s ~/Documents/GitHub/ngoi-stack/principles.md ~/.claude/CLAUDE.md
```

## Install

```sh
claude plugin marketplace add ~/Documents/GitHub/ngoi-stack
claude plugin install ngoi@ngoi-local
```

Run once per Claude Code profile, with `CLAUDE_CONFIG_DIR` set for each.

## Update

Claude Code runs a cached copy. After editing, bump `version` in `.claude-plugin/plugin.json` and `marketplace.json`, then in each profile:

```sh
claude plugin marketplace update ngoi-local
claude plugin update ngoi@ngoi-local
```

## Test

```sh
python3 -m unittest tests/test_guard.py
claude plugin validate .
```

See [CREDITS.md](CREDITS.md) for what came from superpowers, pstack and GSD Core.
