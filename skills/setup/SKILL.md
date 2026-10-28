---
name: setup
description: Prepare a repo for ngoi once. Writes a local check script and a verify guide that lets an agent run the app and use it like a real user. Use when the user types /ngoi:setup, or when ngoi build finds a repo without .ngoi/check.
---

# Setup

Every ngoi review depends on two local files:

- `.ngoi/check` runs typecheck, lint and tests. Exit 0 means green.
- `.ngoi/verify.md` tells an agent how to launch the app, use it like a user, and capture proof.

Everything ngoi writes lives in `.ngoi/`, and `.ngoi/` stays out of git. Never edit `.gitignore` and never commit anything here.

## Steps

1. Append `.ngoi/` to `.git/info/exclude` if it isn't there.
2. Read the repo before asking anything: package scripts, Makefile, README, CI workflows, docker-compose, env examples. Ask the user only what you can't observe, such as credentials or which surface matters most.
3. Write `.ngoi/check` as an executable bash script with `set -euo pipefail`. Reuse the commands CI runs. Print each step. If the repo has no tests or lint, run what exists and say so.
4. Write `.ngoi/verify.md` with these sections, using real commands from this repo, never placeholders:
   - **Surface.** Web UI, API, CLI or library. For a library, driving means a scratch script that imports the public API.
   - **Launch.** Exact commands, on a free port picked at launch (never a fixed port another process might hold) and its own local database or data dir, so it never touches the user's dev session or a remote database. Migrations and seed data included. Ready means a real request succeeds, not just that a process started. Refuse to launch if the database URL points at a non-local host.
   - **Dependencies.** Other repos or services to start first, with absolute paths. Needed when work spans repos.
   - **Health check.** One read-only command that confirms the instance is ours and alive.
   - **Drive.** Web: `agent-browser` (open, snapshot, click by accessible name, fill, screenshot). API: `curl` with real routes. CLI: commands and input. Prefer stable handles over coordinates.
   - **Evidence.** What to capture (screenshot, response body, database query, log line, exit code) and where: `.ngoi/evidence/<topic>/`. Capture the action and the resulting state, including side effects.
   - **Cleanup.** Stop only what you started. Keep the evidence.
   - **Journeys.** The 3 to 6 main things a user does. For each: how a user gets there, how to drive it, and the end state that proves it works.
5. Prove it. Run `.ngoi/check` once and report the result honestly, red included. Don't fix code here. Then launch, run the health check, drive one journey, capture evidence and clean up. Confirm the evidence survived cleanup. Fix the guide until this works. A guide nobody ran is a draft.
6. For a new app with nothing to run yet, write what exists and mark Launch as pending. The build's first unit completes it.

**Reply:** what `check` runs and its current result, the surface, the journey you proved with its evidence path, and anything you couldn't automate.
