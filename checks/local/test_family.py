"""Unit tests for the family audit and the map check: python3 -m unittest discover -s checks/local"""
import io
import json
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import family_audit
import family_members
import map_true

PAGE = """| Member | Problem | State |
|---|---|---|
| [alpha](https://github.com/Tewf/alpha) | the standard | v1.2.3, done |
| [beta](https://github.com/Tewf/beta) | a thing | scope only |
Not a row.
"""


class Members(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.readme = Path(self.dir.name) / "README.md"
        self.readme.write_text(PAGE)

    def tearDown(self):
        self.dir.cleanup()

    def test_reads_rows_in_order(self):
        names = [(m.name, m.state) for m in family_members.read_members(self.readme)]
        self.assertEqual(names, [("alpha", "v1.2.3, done"), ("beta", "scope only")])

    def test_missing_file_gives_none(self):
        self.assertEqual(family_members.read_members(self.readme.with_name("none.md")), [])

    def test_version_in(self):
        self.assertEqual(family_members.version_in("v0.6.1"), (0, 6, 1))
        self.assertIsNone(family_members.version_in("scope only"))


class Audit(unittest.TestCase):
    def test_parse_output(self):
        out = "judgment: 5 question(s), 3 answered in x, backend none\n1 error(s), 4 warning(s); tiers run: program\n"
        self.assertEqual(family_audit.parse_output(out), (1, 4, 2))

    def test_parse_without_totals(self):
        self.assertIsNone(family_audit.parse_output("Traceback"))

    def test_exit_code_fails_only_on_errors(self):
        ok = family_audit.Result("a", 0, 3, 1)
        gone = family_audit.Result("b", None, None, None, "clone failed")
        bad = family_audit.Result("c", 2, 0, 0)
        self.assertEqual(family_audit.exit_code([ok, gone]), 0)
        self.assertEqual(family_audit.exit_code([ok, bad]), 1)

    def test_table(self):
        text = family_audit.table([family_audit.Result("a", 0, 3, 1), family_audit.Result("b", None, None, None, "x")])
        self.assertIn("| a | 0 | 3 | 1 |", text)
        self.assertIn("unreachable", text)

    def test_audit_member_with_a_fake_standard(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "std" / "checks").mkdir(parents=True)
            (tmp / "std" / "checks" / "run.py").write_text("print('2 error(s), 1 warning(s); tiers run: program')\n")
            work = tmp / "work"
            (work / "m").mkdir(parents=True)  # already "cloned"
            member = family_members.Member("m", "Tewf", "https://github.com/Tewf/m", "v1.0.0", 1)
            result = family_audit.audit_member(member, tmp / "std", work)
            self.assertEqual((result.errors, result.warnings), (2, 1))

    def test_failed_clone_is_unreachable_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            member = family_members.Member("m", "Tewf", "file:///nonexistent/repo", "v1", 1)
            result = family_audit.audit_member(member, Path(tmp), Path(tmp) / "w", clone_timeout=20)
            self.assertIsNone(result.errors)

    def test_inactive_check_finds_nothing(self):
        self.assertEqual(family_audit.check(Path("."), {"online": True}), [])


class MapTrue(unittest.TestCase):
    def test_newest_tag_ignores_non_versions(self):
        self.assertEqual(map_true.newest_tag(["v1.9.0", "v1.10.0", "nightly", "v0.1.0"]), (1, 10, 0))
        self.assertIsNone(map_true.newest_tag(["nightly"]))

    def test_compare(self):
        self.assertIsNone(map_true.compare("v1.0.0", ["v1.0.0"]))
        self.assertIsNone(map_true.compare("scope only", []))
        self.assertIn("v1.0.0", map_true.compare("v0.9.0", ["v1.0.0"]))
        self.assertIn("v0.9.0", map_true.compare("v0.9.0", []))

    def run_check(self, fetch, online=True):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "README.md").write_text(PAGE)
            return map_true.check(Path(tmp), {"online": online}, fetch=fetch)

    def test_offline_run_finds_nothing(self):
        self.assertEqual(self.run_check(lambda o, n: self.fail("no request"), online=False), [])

    def test_mismatch_is_a_warning_with_both_values(self):
        found = self.run_check(lambda o, n: ["v1.3.0"] if n == "alpha" else [])
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].kind, "warning")
        self.assertIn("v1.2.3", found[0].message)
        self.assertIn("v1.3.0", found[0].message)

    def test_failed_request_is_a_warning_not_a_crash(self):
        def boom(owner, name):
            raise urllib.error.URLError("network unreachable")
        found = self.run_check(boom)
        self.assertEqual(len(found), 2)
        self.assertTrue(all("not reached" in f.message and f.kind == "warning" for f in found))

    def test_fetch_tags_reads_the_api_shape(self):
        body = io.BytesIO(json.dumps([{"name": "v1.0.0"}, {"name": "v0.9.0"}]).encode())
        opened = lambda request, timeout: body
        self.assertEqual(map_true.fetch_tags("o", "n", opener=opened), ["v1.0.0", "v0.9.0"])

    def test_fetch_tags_rejects_an_error_object(self):
        opened = lambda request, timeout: io.BytesIO(b'{"message": "rate limited"}')
        with self.assertRaises(ValueError):
            map_true.fetch_tags("o", "n", opener=opened)


if __name__ == "__main__":
    unittest.main()
