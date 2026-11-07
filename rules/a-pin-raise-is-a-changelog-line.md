# A pin raise is a changelog line

**Rule:** Moving to a new release of the standard is one line in `CHANGELOG.md`, not a decision record, and it moves every workflow at once.

**Grade:** convention.

## Why

- A record holds a choice that had alternatives; a pin move had none.
- A repository pins the standard in every workflow that checks it out. Raising only one left two sites on an old stylesheet through seven releases.
- Search all workflows for the old commit, not one file.

## History

- 2026-10-29: two sites loaded a stylesheet seven releases old because only `checks.yml` was raised.
- 2026-10-29: `standard-pin` was added in v1.12.0 and `standard-links` in v1.13.0.
- v1.17.0: the changelog, `changelog-pin` and rule 5 of the [decision record shape](https://github.com/Tewf/reader-ergonomics/blob/a67087a2cf4c9a552b6ec4bd96e90bec838e8859/shapes/decision-record.md) were added.
- Past pin records stay, since `decision-records` forbids gaps.

## See also

[The rules](README.md); [the front page](../README.md).
