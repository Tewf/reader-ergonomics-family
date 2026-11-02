# Every member has a release a reader can copy from

**Rule:** Every member is tagged `vMAJOR.MINOR.PATCH` and its front page opens with a take-it block: copy the shape, pin the standard by commit, run the checks, say where a disagreement goes.

**Grade:** convention.

## Why

- A reader who wants to use a member needs a fixed version, not a moving branch.
- A tag can move and a commit cannot, so pins name the commit and the tag is a comment beside it.
- A major version can break an extension and is decided first; a minor or patch is released once the checks pass.

## History

- 2026-10-29: the standard reached v1.19.1 and four extensions v1.0.0; topic stood at v0.6.1.
- 2026-10-29: each owner tested the take-it path from an empty folder against GitHub.
- The `map-true` check compares this page's State column with each member's newest tag every week.

## See also

[The rules](README.md); [the front page](../README.md).
