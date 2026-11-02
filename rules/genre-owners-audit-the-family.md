# Each genre owner audits the whole family

**Rule:** The owner of a genre audits every member in that genre; a finding goes to the owning repository as an issue, never as a push.

**Grade:** convention.

## Why

- The owner knows the genre's principles best and sees the most violations.
- A push into another member's repository skips that member's own checks and review.
- A finding a program can decide becomes a check, tested in the genre's repository and then proposed to the standard.

## History

- 2026-10-29: six readers each audited the family in their genre. Evidence was clean everywhere; front pages were false or stale in five of six.
- 2026-10-29: the audit was done by hand and with one script per genre.
- 2026-11-02: [the family audit](../checks/local/family_audit.py) runs the standard's checks on every member weekly, so the audit is repeated rather than remembered.

## See also

[The rules](README.md); [the front page](../README.md).
