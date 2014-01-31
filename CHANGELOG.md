# Changelog

All notable changes to SloBudget are documented here. The format follows Keep a
Changelog, and the project uses semantic versioning.

## [Unreleased]

### Changed

- Alert wording for the burn-rate windows is under review.

## [1.0.1] - 2026-07-08

### Fixed

- The burn rate for a gap window is now computed against the window length,
  not the whole sample range.

## [1.0.0] - 2025-11-25

### Added

- Stable CLI contract for sli, burn, alerts, and version, exit codes 0/1/2.
- Tests pin the window arithmetic at the edges.

## [0.9.0] - 2023-10-09

### Added

- Report renderer with the budget burndown view.
- JSON output for pipeline use.

## [0.8.0] - 2022-01-24

### Added

- Alert thresholds for fast and slow burn windows.
- Gap detection for missing samples.

## [0.7.0] - 2020-06-15

### Added
