#!/usr/bin/env python3
"""ngoi guard: refuse edits that weaken checks, and commands that can't be undone.

Reads a Claude Code PreToolUse event on stdin and prints a deny decision, or nothing.
Only text an edit adds is checked, so removing a suppression always passes.
"""
import json
import os
import re
import sys
from collections import Counter

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

DOC_FILE = re.compile(r"\.(md|mdx|txt|rst)$")
TEST_FILE = re.compile(
    r"(^|/)(tests?|__tests__)/|(^|/)test_[^/]*\.py$|_test\.py$|\.(test|spec)\.[cm]?[jt]sx?$"
)
GATE_FILE = re.compile(r"(^|/)\.ngoi/(check$|verify\.md$|verify/)")
EVIDENCE_FILE = re.compile(r"(^|/)\.ngoi/evidence/")
CONFIG_FILE = re.compile(
    r"(^|/)(tsconfig[^/]*\.json|jsconfig\.json|\.eslintrc[^/]*|eslint\.config\.[cm]?[jt]s"
    r"|pyproject\.toml|\.?ruff\.toml|mypy\.ini|setup\.cfg|\.flake8)$|(^|/)\.github/workflows/"
)

SUPPRESSIONS = [
    (r"eslint-disable", "an eslint-disable"),
    (r"@ts-(ignore|expect-error|nocheck)", "a TypeScript suppression"),
    (r"#\s*type:\s*ignore", "a `# type: ignore`"),
    (r"#\s*noqa\b", "a `# noqa`"),
    (r"pragma:\s*no\s*cover|istanbul ignore", "a coverage exclusion"),
    (r"\bas unknown as\b", "an `as unknown as` cast"),
    (r"catch\s*(\([^)]*\))?\s*\{\s*\}", "an empty catch block"),
]
SKIPPED_TESTS = [
    (r"\.(skip|only)\s*\(", "a skipped or focused test"),
    (r"\bx(it|describe|test)\s*\(", "a skipped test"),
    (r"@pytest\.mark\.(skip|xfail)|pytest\.skip\(|@unittest\.skip", "a skipped test"),
]
DEBT = re.compile(r"\b(TBD|FIXME|XXX)\b")
TICKET = re.compile(r"#\d+|\b[A-Z][A-Z0-9]+-\d+\b")
LOOSENING = [
    r'"(strict\w*|noImplicit\w+|noUnused\w+|noUnchecked\w+|noFallthrough\w+|exactOptionalPropertyTypes)"\s*:\s*false',
    r'["\'][\w@/-]+["\']\s*:\s*(["\'](off|warn)["\']|[01])\s*,?\s*$',
    r"\b(ignorePatterns|ignores)\b",
    r"^\s*(extend-)?ignore\s*=|per-file-ignores",
    r"\b(ignore_errors|ignore_missing_imports)\s*=\s*true",
    r"\b(strict|disallow_\w+|check_untyped_defs|warn_\w+)\s*=\s*false",
    r"continue-on-error:\s*true|\|\|\s*true\b",
]

LOCAL_HOST = r"(localhost|127\.0\.0\.1|\[::1\]|0\.0\.0\.0)\b"
BASH_RULES = [
    (r"\bgit\s+push\b[^;&|]*\s(-f\b|--force)",
     "Force-pushing rewrites history. Push without force, or ask the user to do it."),
    (r"\b(fly|flyctl)\s+deploy\b|\bvercel\b[^;&|]*\s--prod\b|\b(npm|pnpm|yarn)\s+publish\b"
     r"|\bterraform\s+(apply|destroy)\b|\bkubectl\s+(apply|delete)\b|\bsupabase\s+db\s+(push|reset)\b",
     "Deploying and publishing stay with the user. Say what to run and why."),
    (r"(?i)\bdrop\s+(table|database|schema)\b|\btruncate\s+table\b",
     "Destructive SQL deletes data. Use a migration the user reviews, or ask the user."),
    (rf"postgres(ql)?://[^\s'\"]*@(?!{LOCAL_HOST})[\w.-]+|\bpsql\b[^;&|]*\s-h\s*(?!{LOCAL_HOST})[\w.-]+",
     "This command touches a non-local database. Give the user the exact read-only query "
     "to run themselves with the `!` prefix, and work from their output."),
]


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": f"ngoi guard: {reason}",
    }}))
    sys.exit(0)


def added_lines(old, new):
    remaining = Counter(old.splitlines())
    added = []
    for line in new.splitlines():
        if remaining[line]:
            remaining[line] -= 1
        else:
            added.append(line)
    return added


def edit_texts(tool, inp, path):
    """Return (old, new) text pairs for an edit and whether it creates a file."""
    if tool == "Edit":
        return [(inp.get("old_string", ""), inp.get("new_string", ""))], False
    if tool == "MultiEdit":
        return [(e.get("old_string", ""), e.get("new_string", "")) for e in inp.get("edits", [])], False
    if tool == "NotebookEdit":
        return [("", inp.get("new_source", ""))], False
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return [(f.read(), inp.get("content", ""))], False
    except OSError:
        return [("", inp.get("content", ""))], True


def inside_ngoi_source(real):
    """True for files of the ngoi plugin itself, whose patterns and tests name every tell."""
    if real.startswith(PLUGIN_ROOT + os.sep):
        return True
    folder = os.path.dirname(real)
    while folder != os.path.dirname(folder):
        manifest = os.path.join(folder, ".claude-plugin", "plugin.json")
        if os.path.isfile(manifest):
            try:
                with open(manifest) as f:
                    return json.load(f).get("name") == "ngoi"
            except (OSError, ValueError):
                return False
        folder = os.path.dirname(folder)
    return False


def check_edit(tool, inp, agent):
    path = inp.get("file_path") or inp.get("notebook_path") or ""
    if path and inside_ngoi_source(os.path.realpath(path)):
        return

    if agent and GATE_FILE.search(path):
        deny("`.ngoi/check` and `.ngoi/verify` are the user's gates. Report the change you need instead.")
    if "verifier" in agent and not (TEST_FILE.search(path) or EVIDENCE_FILE.search(path)):
        deny("The verifier writes only tests and evidence, never implementation code.")
    if DOC_FILE.search(path):
        return

    pairs, is_new = edit_texts(tool, inp, path)
    added = [line for old, new in pairs for line in added_lines(old, new)]
    fix = "Fix the cause instead. If it is truly needed, stop and report it as a concern for the user."

    for line in added:
        for pattern, name in SUPPRESSIONS:
            if re.search(pattern, line):
                deny(f"This adds {name}. {fix}")
        if DEBT.search(line) and not TICKET.search(line):
            deny("This adds a TBD/FIXME/XXX with no issue reference. Do the work now, or report it.")
        if TEST_FILE.search(path):
            for pattern, name in SKIPPED_TESTS:
                if re.search(pattern, line):
                    deny(f"This adds {name}. {fix}")
        if not is_new and CONFIG_FILE.search(path):
            for pattern in LOOSENING:
                if re.search(pattern, line):
                    deny(f"This loosens lint, type or CI config. {fix}")


def check_bash(command):
    for pattern, reason in BASH_RULES:
        if re.search(pattern, command):
            deny(reason)
    if re.search(r"\b(rm|unlink)\b|\bgit\s+rm\b", command):
        if any(TEST_FILE.search(token.strip("'\"")) for token in command.split()):
            deny("This deletes tests. A failing test is evidence. Fix the code, or report why the test is wrong.")


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    tool = event.get("tool_name", "")
    inp = event.get("tool_input") or {}
    agent = (event.get("agent_type") or "").lower()
    if tool == "Bash":
        check_bash(inp.get("command", ""))
    elif tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        check_edit(tool, inp, agent)


if __name__ == "__main__":
    main()
