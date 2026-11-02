"""The family's members, read from the State table of the front page.

Not a check (no NAME): the audit and the map check share it. Time O(text).
A member is a table row whose first cell is a link to github.com/<owner>/<name>.
"""
from __future__ import annotations

import re
from typing import NamedTuple
from pathlib import Path

ROW = re.compile(r"^\|\s*\[([^\]]+)\]\((https://github\.com/([^/\s)]+)/([^/\s)]+))\)\s*\|(.*)\|\s*([^|]*?)\s*\|\s*$")
VERSION = re.compile(r"\bv(\d+)\.(\d+)\.(\d+)\b")


class Finding(NamedTuple):
    """Stand-in with the standard's fields, used only when the standard's runner is absent."""
    check: str
    path: str
    line: int
    message: str
    kind: str = "error"


class Member(NamedTuple):
    name: str
    owner: str
    url: str
    state: str
    line: int


def read_members(readme: Path) -> list[Member]:
    """Every member named in the table, in page order; a missing file gives no members."""
    try:
        text = readme.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    members = []
    for number, line in enumerate(text.splitlines(), 1):
        match = ROW.match(line)
        if match:
            members.append(Member(name=match.group(4), owner=match.group(3), url=match.group(2),
                                  state=match.group(6), line=number))
    return members


def version_in(state: str) -> tuple[int, int, int] | None:
    """The first vX.Y.Z in a State cell, or None when the cell names no version."""
    match = VERSION.search(state)
    return tuple(int(part) for part in match.groups()) if match else None
