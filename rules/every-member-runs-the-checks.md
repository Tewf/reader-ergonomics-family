# Every member runs the standard's checks

**Rule:** CI on each member runs the standard's checks, and the member's own checks sit in `checks/local/`. The standard adopts an extension's check once it holds across the family.

**Grade:** convention.

## Why

- Extensions run only the standard's checks and their own, and siblings never depend on siblings.
- Promotion through the standard is the only route by which one extension's check reaches the others.
- Every member then runs it from its next pin raise.

## History

- 2026-10-29: the interface was published in [extending.md](https://github.com/Tewf/reader-ergonomics/blob/65e42472e2d4cbfd994c2a86e95a47e5dc7301ca/extending.md): a local check defines `NAME` and `check(root, config)`.
- 2026-10-29: `figure-width` was proposed by the presentations extension and adopted in v1.4.0.
- 2026-10-29: `judgment-quotes` was merged from two extensions' local checks in v1.2.0.
- 2026-11-02: the family audit and the map check, in [checks/local/](../checks/local/), run this rule on the whole family each week.

## See also

[The rules](README.md); [the front page](../README.md).
