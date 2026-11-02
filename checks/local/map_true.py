"""Map true: each member's newest tag on GitHub against the State column of the front page.

Online only: it runs when the standard's runner is given `--online`, and finds nothing otherwise. For each member
named in the front page's table it asks the GitHub API for the repository's tags (unauthenticated, no token, the
default User-Agent), takes the highest version, and compares it with the version in the State cell.

A warning (heuristic: a tag is not always a state) when:
- the two versions differ (the message gives both);
- the State names no version but a tag exists, or names a version and no tag exists;
- GitHub could not be reached for a member: the message says why, and nothing is compared.

Time O(members) requests, each with a short timeout. An HTTP error, a timeout or a malformed answer is a warning,
never a crash.

What a clean run guarantees: for every member reached, the State cell and the newest tag agree.
What it does not: that a tag is released, that the state's words are true, or anything about a member not reached.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from family_members import read_members, version_in  # noqa: E402

try:
    from framework.check_api import Finding
except ImportError:  # in the unit tests, outside the standard's runner
    from family_members import Finding

NAME = "map-true"
EXACT = False

API = "https://api.github.com/repos/{owner}/{name}/tags?per_page=100"
TAG = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def newest_tag(tag_names: list[str]) -> tuple[int, int, int] | None:
    """The highest MAJOR.MINOR.PATCH among the names; names that are not versions are ignored."""
    versions = [tuple(int(p) for p in m.groups()) for m in map(TAG.match, tag_names) if m]
    return max(versions) if versions else None


def fetch_tags(owner: str, name: str, opener=urllib.request.urlopen, timeout: int = 10) -> list[str]:
    """Tag names of a repository; raises OSError, ValueError on any failure."""
    request = urllib.request.Request(API.format(owner=owner, name=name), headers={"Accept": "application/vnd.github+json"})
    with opener(request, timeout=timeout) as response:
        data = json.load(response)
    if not isinstance(data, list):
        raise ValueError("unexpected answer from the API")
    return [item["name"] for item in data if isinstance(item, dict) and "name" in item]


def show(version: tuple[int, int, int] | None) -> str:
    return "v" + ".".join(map(str, version)) if version else "none"


def compare(state: str, tags: list[str]) -> str | None:
    """A message when the State cell and the newest tag disagree, else None."""
    stated, held = version_in(state), newest_tag(tags)
    if stated == held:
        return None
    return f"State says {show(stated)} ({state!r}), GitHub's newest tag is {show(held)}"


def check(root: Path, config: dict, fetch=fetch_tags) -> list:
    if not config.get("online"):
        return []
    findings = []
    timeout = config.get("map_true", {}).get("timeout_seconds", 10)
    for member in read_members(root / "README.md"):
        try:
            tags = fetch(member.owner, member.name) if fetch is not fetch_tags else fetch(member.owner, member.name, timeout=timeout)
        except (OSError, ValueError) as error:
            findings.append(Finding(NAME, "README.md", member.line, f"{member.name}: GitHub not reached ({error}); nothing compared", "warning"))
            continue
        message = compare(member.state, tags)
        if message:
            findings.append(Finding(NAME, "README.md", member.line, f"{member.name}: {message}", "warning"))
    return findings
