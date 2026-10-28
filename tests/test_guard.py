import json
import os
import subprocess
import sys
import tempfile
import unittest

GUARD = os.path.join(os.path.dirname(__file__), "..", "hooks", "guard.py")
WORK = tempfile.mkdtemp(prefix="ngoi-guard-")


def run(tool, agent="", **tool_input):
    event = {"tool_name": tool, "tool_input": tool_input}
    if agent:
        event["agent_type"] = agent
    out = subprocess.run([sys.executable, "-I", GUARD], input=json.dumps(event),
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out.strip() else "allow"


def path(name):
    return os.path.join(WORK, name)


def existing(name, content):
    full = path(name)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    return full


def edit(name, old, new, **kw):
    return run("Edit", file_path=path(name), old_string=old, new_string=new, **kw)


class Suppressions(unittest.TestCase):
    def test_adding_suppressions_is_refused(self):
        for line in ["x = f()  # type: ignore", "import os  # noqa: F401", "// eslint-disable-next-line",
                     "// @ts-ignore", "const a = b as unknown as C", "try { go() } catch (e) {}"]:
            with self.subTest(line=line):
                self.assertEqual(edit("app/main.ts", "x", "x\n" + line), "deny")

    def test_removing_or_keeping_a_suppression_passes(self):
        self.assertEqual(edit("app/main.py", "x = f()  # type: ignore", "x = f()"), "allow")
        self.assertEqual(edit("app/main.py", "y = 1\nx = f()  # type: ignore", "y = 2\nx = f()  # type: ignore"), "allow")

    def test_plain_code_passes(self):
        self.assertEqual(edit("app/main.py", "a = 1", "a = 2"), "allow")

    def test_docs_may_mention_suppressions(self):
        self.assertEqual(edit("README.md", "", "Never add `# type: ignore`."), "allow")


class DebtMarkers(unittest.TestCase):
    def test_bare_marker_is_refused(self):
        self.assertEqual(edit("app/main.py", "a", "a  # TODO later\n# FIXME handle timeout"), "deny")

    def test_marker_with_ticket_passes(self):
        self.assertEqual(edit("app/main.py", "a", "a\n# FIXME handle timeout #123"), "allow")
        self.assertEqual(edit("app/main.py", "a", "a\n# TBD see ENG-42"), "allow")


class SkippedTests(unittest.TestCase):
    def test_skips_in_test_files_are_refused(self):
        self.assertEqual(edit("web/cart.test.ts", "it(", "it.skip("), "deny")
        self.assertEqual(edit("tests/test_totals.py", "def", "@pytest.mark.skip\ndef"), "deny")

    def test_orm_only_outside_tests_passes(self):
        self.assertEqual(edit("app/queries.py", "qs", "qs.only('id')"), "allow")


class Config(unittest.TestCase):
    def test_loosening_existing_config_is_refused(self):
        existing("tsconfig.json", '{"compilerOptions": {"strict": true}}')
        self.assertEqual(run("Edit", file_path=path("tsconfig.json"), old_string='"strict": true',
                             new_string='"strict": false'), "deny")
        existing("pyproject.toml", "[tool.ruff]\n")
        self.assertEqual(run("Edit", file_path=path("pyproject.toml"), old_string="[tool.ruff]",
                             new_string='[tool.ruff]\nignore = ["E501"]'), "deny")

    def test_ordinary_config_edit_passes(self):
        existing("tsconfig.app.json", '{"compilerOptions": {}}')
        self.assertEqual(run("Edit", file_path=path("tsconfig.app.json"), old_string="{}",
                             new_string='{"paths": {"@/*": ["src/*"]}}'), "allow")

    def test_new_config_file_from_a_scaffold_passes(self):
        self.assertEqual(run("Write", file_path=path("fresh/eslint.config.js"),
                             content="export default [{ ignores: ['dist'] }]"), "allow")


class Gates(unittest.TestCase):
    def test_subagent_cannot_edit_gates(self):
        self.assertEqual(run("Write", agent="ngoi:implementer", file_path=path(".ngoi/check"), content="exit 0"), "deny")

    def test_main_session_can_write_gates(self):
        self.assertEqual(run("Write", file_path=path(".ngoi/verify.md"), content="# Verify"), "allow")

    def test_verifier_writes_only_tests_and_evidence(self):
        self.assertEqual(run("Write", agent="ngoi:verifier", file_path=path("app/main.py"), content="x"), "deny")
        self.assertEqual(run("Write", agent="ngoi:verifier", file_path=path("tests/test_new.py"), content="x"), "allow")
        self.assertEqual(run("Write", agent="ngoi:verifier", file_path=path(".ngoi/evidence/a/log.txt"), content="x"), "allow")


class OwnSource(unittest.TestCase):
    def test_the_ngoi_repo_may_name_every_tell(self):
        own = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixture.py")
        self.assertEqual(run("Edit", file_path=own, old_string="a", new_string="a  # type: ignore"), "allow")


class Commands(unittest.TestCase):
    def test_irreversible_commands_are_refused(self):
        for command in ["git push --force origin main", "git push -f", "fly deploy", "vercel deploy --prod",
                        "npm publish", "psql -c 'DROP TABLE users'",
                        "psql postgres://u:p@db.prod.example.com:5432/app -c 'select 1'",
                        "psql -h db.prod.example.com app", "rm tests/test_totals.py", "git rm web/cart.test.ts"]:
            with self.subTest(command=command):
                self.assertEqual(run("Bash", command=command), "deny")

    def test_everyday_commands_pass(self):
        for command in ["git push -u origin ngoi/totals", "pytest -q", "rm -rf dist",
                        "psql postgres://u:p@localhost:5432/app -c 'select 1'", "npm run build"]:
            with self.subTest(command=command):
                self.assertEqual(run("Bash", command=command), "allow")


if __name__ == "__main__":
    unittest.main()
