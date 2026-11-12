# 0002: The family audit is a program in this repository

**Decision:** the audit of every member is a local check here, run weekly by a workflow, and not a check of the
standard.

**Status:** accepted, 2026-11-02. **Shape:** [decision record](https://github.com/Tewf/reader-ergonomics/blob/65e42472e2d4cbfd994c2a86e95a47e5dc7301ca/shapes/decision-record.md).

## Context

- On 2026-10-29 each genre owner audited the family by hand and with one script per genre.
- The standard depends on no extension ([rule](../rules/standard-depends-on-no-extension.md)), so it cannot hold a check
  that clones and runs its extensions.
- Alternatives: a script in each extension; a job in the standard; a program in this repository.

## Decision

- [family_audit.py](../checks/local/family_audit.py) clones every member named in the State table, runs the standard's
  program tier on it, and writes one table of errors, warnings and open questions.
- It fails only when a member has errors. A member it cannot reach is reported, not failed.
- It runs weekly and on demand, and as a registered check only when asked for online.

## Consequences

- The audit is repeated by CI rather than remembered, and the table is read from one place.
- **Bad:** it runs each member's own local checks, which is code from that member; it is safe only for members of this family.
- The meaning and syntax tiers are left to each member's own CI.

## See also

[Decisions](README.md); [the workflow](../.github/workflows/family-audit.yml).
