# Changelog

All notable changes to this project are documented here. This project follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Add playlist scoring and automatic workout ordering.

## [0.8.0] - 2026-07-21

### Added

- Persistent SQLite music catalog with unique path-based track upserts.
- Text search and filters for BPM, energy, key, mode, format, and tags.
- Case-insensitive many-to-many tags that survive track re-indexing.
- `library index`, `search`, `tag`, `untag`, and `tags` CLI commands.
- Public `LibraryCatalog`, `LibraryQuery`, and `index_directory` engine APIs.

### Changed

- Added `data/library/` as ignored durable local application data.

## [0.7.0] - 2026-07-21

### Added

- Major/minor musical-key detection using harmonic CQT chroma profiles.
- Key confidence, Camelot notation, and Open Key notation.
- Same-key, adjacent-wheel, and relative-mode compatibility suggestions.
- `--key` option for single-track and batch CLI analysis.
- Musical-key fields in cache, JSON, and CSV reports.

### Changed

- Key analysis uses a downsampled 60-second middle segment to bound memory.
- Upgraded the analysis cache schema for musical-key profiles.

## [0.6.0] - 2026-07-21

### Added

- Explainable perceptual energy score from 1–10 and descriptive levels.
- Configurable energy timeline sections that default to 15 seconds.
- RMS loudness, onset activity, and spectral-brightness component metrics.
- `--energy` and `--energy-section-seconds` options for analyze and batch CLI.
- Energy values and sections in cache, JSON, and CSV reports.

### Changed

- Tempo and energy analysis now share a single audio decode operation.
- Upgraded the analysis cache schema for energy-aware profiles.

## [0.5.0] - 2026-07-21

### Added

- Raw and octave-normalized BPM values with configurable tempo ranges.
- BPM confidence score and low, medium, or high confidence level.
- Normalized beat-grid positions, beat count, and first-beat timing.
- Tempo details in JSON and CSV reports and human-readable CLI output.

### Changed

- Upgraded the analysis cache schema to invalidate legacy BPM-only results.

## [0.4.0] - 2026-07-21

### Added

- Directory-level batch audio analysis with per-track error isolation.
- Persistent cache with file and analysis-profile invalidation.
- UTF-8 JSON and Excel-friendly CSV analysis reports.
- `batch` CLI command with report, cache, and metadata-only options.
- Cache warnings and machine-readable error details in batch results.

## [0.3.0] - 2026-07-20

### Added

- Reusable `TrackMetadata` and `TrackAnalysis` result contracts.
- Local audio metadata and duration inspection powered by Mutagen.
- Optional BPM estimation powered by librosa.
- `scan` and `analyze` CLI commands, including JSON output.
- Automated coverage for metadata, BPM-adapter normalization, and result
  behavior.

## [0.2.0] - 2026-07-20

### Added

- Professional `src/` package layout.
- Repository standards, contributor policy, security policy, and MIT license.
- Pytest and Ruff configuration with PowerShell maintenance scripts.
- GitHub Actions workflows, Dependabot configuration, issue forms, and a pull
  request template.
- Documentation for installation, development, architecture, roadmap, FAQ, and
  architecture decision records.

### Changed

- Moved local input, output, report, and cache directories under `data/`.
- Moved the existing music scanner into `src/aerobictoolkit/analysis/`.

[Unreleased]: https://github.com/somphong-git/Work-AerobicToolkit/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/somphong-git/Work-AerobicToolkit/releases/tag/v0.8.0
[0.7.0]: https://github.com/somphong-git/Work-AerobicToolkit/releases/tag/v0.7.0
[0.6.0]: https://github.com/somphong-git/Work-AerobicToolkit/releases/tag/v0.6.0
[0.5.0]: https://github.com/somphong-git/Work-AerobicToolkit/releases/tag/v0.5.0
[0.4.0]: https://github.com/somphong-git/Work-AerobicToolkit/releases/tag/v0.4.0
[0.3.0]: https://github.com/somphong-git/Work-AerobicToolkit/releases/tag/v0.3.0
[0.2.0]: https://github.com/somphong-git/Work-AerobicToolkit/releases/tag/v0.2.0
