"""Family audit: run the standard's program-tier checks on every member named in the front page, and report.

Run it by hand or from the weekly workflow:

    python3 checks/local/family_audit.py --standard path/to/reader-ergonomics [--summary FILE] [--workdir DIR]

For each member it clones the default branch (depth 1, no credentials), runs the standard's `checks/run.py` with
`--tiers program --judge none`, and reads the last lines for the errors, the warnings and the open questions. It
writes one table (member, errors, warnings, questions) to `--summary` (in CI, the job summary) and to the output.
It exits 1 when a member has errors, when a member's run gives no totals (the standard could not judge it), or when no
member could be cloned at all; a member that cannot be cloned while others can is a warning. Before issue #1 it
exited 0 in the last two cases, so an audit that read no member was green.

As a registered check it does nothing unless the environment sets FAMILY_AUDIT=1 and the run is online, because it
clones the whole family; then each member with errors is one error finding.
Time O(members x the standard's checks); network: one clone per member.

What a clean run guarantees: every member that could be cloned has no exact finding in the program tier.
What it does not: anything the meaning and syntax tiers find, or a member it could not reach.

The run executes code from each cloned member's `checks/local/` (the standard's runner loads it): trust only
members of this family.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from typing import NamedTuple
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from family_members import Member, read_members  # noqa: E402

try:
    from framework.check_api import Finding
except ImportError:  # run by hand or in the unit tests, outside the standard's runner
    from family_members import Finding

NAME = "family-audit"
EXACT = True

TOTALS = re.compile(r"(\d+) error\(s\), (\d+) warning\(s\)")
QUESTIONS = re.compile(r"judgment: (\d+) question\(s\), (\d+) answered")


class Result(NamedTuple):
    member: str
    errors: int | None      # None: unreachable
    warnings: int | None
    questions: int | None
    note: str = ""
    stage: str = ""         # where an unreachable member stopped: "clone" or "run"


def parse_output(output: str) -> tuple[int, int, int] | None:
    """(errors, warnings, open questions) from a run's output, or None when the totals line is missing."""
    totals = TOTALS.findall(output)
    if not totals:
        return None
    errors, warnings = (int(n) for n in totals[-1])
    asked = QUESTIONS.findall(output)
    open_questions = max(0, int(asked[-1][0]) - int(asked[-1][1])) if asked else 0
    return errors, warnings, open_questions


def run(command: list[str], timeout: int) -> tuple[int, str]:
    """Run a command; a timeout or a missing program is a return code of -1 and a message, never a crash."""
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return -1, f"timed out after {timeout}s"
    except OSError as error:
        return -1, str(error)
    return done.returncode, done.stdout + done.stderr


def audit_member(member: Member, standard: Path, workdir: Path, clone_timeout: int = 120, check_timeout: int = 600) -> Result:
    target = workdir / member.name
    if not target.is_dir():
        code, message = run(["git", "clone", "--quiet", "--depth", "1", member.url, str(target)], clone_timeout)
        if code != 0:
            note = "clone failed: " + message.strip().splitlines()[-1][:120] if message.strip() else "clone failed"
            return Result(member.name, None, None, None, note, "clone")
    code, output = run([sys.executable, str(standard / "checks" / "run.py"), str(target),
                        "--tiers", "program", "--judge", "none"], check_timeout)
    parsed = parse_output(output)
    if parsed is None:
        return Result(member.name, None, None, None, f"run gave no totals (exit {code})", "run")
    return Result(member.name, *parsed)


def table(results: list[Result]) -> str:
    rows = ["| Member | Errors | Warnings | Questions |", "|---|---|---|---|"]
    for r in results:
        if r.errors is None:
            rows.append(f"| {r.member} | unreachable | unreachable | unreachable ({r.note}) |")
        else:
            rows.append(f"| {r.member} | {r.errors} | {r.warnings} | {r.questions} |")
    return "\n".join(rows) + "\n"


def exit_code(results: list[Result]) -> int:
    """1 when a member that ran has errors, when a run gave no totals, or when every member's clone failed; 0 else."""
    if any(r.errors for r in results) or any(r.stage == "run" for r in results):
        return 1
    return 1 if results and all(r.stage == "clone" for r in results) else 0


def warnings(results: list[Result]) -> list[str]:
    """One GitHub annotation per member that could not be cloned: a warning, unless every clone failed."""
    return [f"::warning::{r.member}: {r.note}" for r in results if r.stage == "clone"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--standard", required=True, type=Path, help="a checkout of the standard")
    parser.add_argument("--readme", type=Path, default=Path(__file__).resolve().parents[2] / "README.md")
    parser.add_argument("--summary", type=Path, help="append the table to this file (CI: the job summary)")
    parser.add_argument("--workdir", type=Path, help="where members are cloned (default: a temporary folder)")
    args = parser.parse_args(argv)
    members = read_members(args.readme)
    if not members:
        print(f"no member found in {args.readme}", file=sys.stderr)
        return 2
    if not (args.standard / "checks" / "run.py").is_file():
        print(f"no checks/run.py under {args.standard}", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory() as scratch:
        workdir = args.workdir or Path(scratch)
        workdir.mkdir(parents=True, exist_ok=True)
        results = [audit_member(m, args.standard, workdir) for m in members]
    text = table(results)
    print(text)
    for line in warnings(results):
        print(line)
    if args.summary:
        with args.summary.open("a", encoding="utf-8") as handle:
            handle.write("## Family audit\n\n" + text)
    return exit_code(results)


def check(root: Path, config: dict) -> list:
    if os.environ.get("FAMILY_AUDIT") != "1" or not config.get("online"):
        return []
    standard = Path(os.environ.get("FAMILY_AUDIT_STANDARD", ""))
    findings, results = [], []
    with tempfile.TemporaryDirectory() as scratch:
        for member in read_members(root / "README.md"):
            result = audit_member(member, standard, Path(scratch))
            results.append(result)
            if result.errors:
                findings.append(Finding(NAME, "README.md", member.line, f"{member.name} has {result.errors} error(s) in the program tier"))
            elif result.stage == "run":
                findings.append(Finding(NAME, "README.md", member.line, f"{member.name}: {result.note}"))
    if results and all(r.stage == "clone" for r in results):
        findings.append(Finding(NAME, "README.md", 1, "no member of the family could be cloned"))
    return findings


if __name__ == "__main__":
    sys.exit(main())
