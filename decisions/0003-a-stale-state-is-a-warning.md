# 0003: A stale State is a warning, not an error

**Decision:** the map check compares each member's newest tag with the State column and reports a mismatch as a
warning that gives both values.

**Status:** accepted, 2026-11-02. **Shape:** [decision record](https://github.com/Tewf/reader-ergonomics/blob/65e42472e2d4cbfd994c2a86e95a47e5dc7301ca/shapes/decision-record.md).

## Context

- A State cell may say words, such as "scope only", where no tag exists, and a tag may be pushed before the page is edited.
- GitHub's unauthenticated API can be slow or rate limited, and the check must not turn that into a red run.
- Alternatives: an error on any mismatch; a warning; no check.

## Decision

- [map_true.py](../checks/local/map_true.py) is a warning check, run only online, with no token and no identity.
- A request that fails is a warning that says why; nothing is compared for that member.

## Consequences

- The page cannot go stale in silence, and a flaky network cannot fail a run.
- **Bad:** a reader who ignores warnings can still leave a State stale; the weekly run lists it each time.

## See also

[Decisions](README.md); [the front page](../README.md), where the State column is.
