# Changelog

The releases this repository pins, newest first, in the form of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
A pin move is recorded here, not in decisions/.

## [0.1.1] - 2026-11-04

### Changed

- Pinned reader-ergonomics v1.21.0 (`2e5b6f0`), from v1.20.0 (`4f99372`): duplication skips the lines a declared shape prescribes
- Pinned reader-ergonomics v1.20.0 (`4f99372`), from v1.19.2 (`b9732b9`): the runner's verdicts file (`--out`), and hand-written llms.txt lines kept through a rebuild
- Tag v0.1.1 and a GitHub release of the same name.

## [0.1.0] - 2026-11-03

### Added

- The first release: the map of the family, each member's state, and the six shared rules, one page each in `rules/`.
- Two programs in `checks/local/` with 17 unit tests: the family audit, which runs every member's checks on every
  member, and the map check, which compares each state with GitHub's tags.
- Three decision records, a weekly audit workflow, and a take-it block on both front pages.
- A step in `checks.yml` that runs the unit tests before the standard's checks.
- Pinned reader-ergonomics v1.19.2 (`b9732b9`), as below.

## 2026-11-02

### Added

- Pinned reader-ergonomics v1.19.2 (`b9732b9`), at the repository's start: the standard's pin, link, changelog and
  decision-record checks, which this skeleton is written to pass.
