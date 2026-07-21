# Changelog

All notable changes to this project are documented here. This project follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Add perceptual energy and intensity-section analysis.

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

[Unreleased]: https://github.com/somphong-git/Work-AerobicToolkit/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/somphong-git/Work-AerobicToolkit/releases/tag/v0.5.0
[0.4.0]: https://github.com/somphong-git/Work-AerobicToolkit/releases/tag/v0.4.0
[0.3.0]: https://github.com/somphong-git/Work-AerobicToolkit/releases/tag/v0.3.0
[0.2.0]: https://github.com/somphong-git/Work-AerobicToolkit/releases/tag/v0.2.0
