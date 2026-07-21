# Work-AerobicToolkit

Work-AerobicToolkit is an open-source, engine-first foundation for aerobic DJ
mix workflows. The same core package is intended to support future CLI,
desktop, web, API, plugin, agent, and mobile interfaces.

> **Project status:** pre-alpha. Sprint 2.6 adds perceptual energy scores and
> section timelines. Playlist generation and mix rendering remain future work.

## Installation

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

See the complete [installation guide](docs/installation.md) for other
platforms and troubleshooting.

## Verify the installation

```powershell
python -m aerobictoolkit --version
python -m aerobictoolkit --help
```

## Analyze audio

Put local tracks in `data/input/`, then scan them or analyze an individual
file. BPM estimation is provided by the optional `analysis` dependency group.

```powershell
python -m pip install -e ".[analysis]"
python -m aerobictoolkit scan data/input
python -m aerobictoolkit analyze "data/input/your-track.mp3" --json
```

Use `--no-bpm` to inspect metadata only.

Tempo is normalized into 90–180 BPM by default to resolve common half-time and
double-time estimates. Results also include a confidence score from 0 to 1 and
the detected beat positions. A custom one-octave range can be supplied:

```powershell
python -m aerobictoolkit analyze "data/input/your-track.mp3" `
  --min-bpm 100 --max-bpm 200
```

Request energy analysis explicitly to receive an overall score from 1–10 and a
15-second timeline:

```powershell
python -m aerobictoolkit analyze "data/input/your-track.mp3" --energy
python -m aerobictoolkit batch data/input --energy
```

Use `--energy-section-seconds 10` to change the timeline resolution. Energy is
opt-in so existing metadata and BPM workflows keep their previous performance.

Analyze every supported track in a folder and write reusable reports:

```powershell
python -m aerobictoolkit batch data/input
```

The default cache is `data/cache/analysis-cache.json`. Reports are written to
`data/reports/analysis-report.json` and `data/reports/analysis-report.csv`.
Run the command again to reuse unchanged results, or append `--no-cache` to
force a fresh analysis.

## Repository layout

```text
src/aerobictoolkit/  Reusable package and future engine modules
tests/               Automated test suite
examples/            Small runnable usage examples
docs/                Architecture, guides, roadmap, and ADRs
data/                Ignored local input, output, reports, and cache data
scripts/             Build, lint, formatting, release, and documentation tools
```

## Development

```powershell
.\scripts\lint.ps1
python -m pytest
```

Read the [developer guide](docs/developer-guide.md) before changing code.

## Project management

Work is planned issue-first: issue → discussion → branch → commit → pull
request → merge. The intended GitHub Project columns are Backlog, Sprint,
Doing, Review, and Done. See [CONTRIBUTING.md](CONTRIBUTING.md) for the
working agreement.

## Documentation

- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Installation](docs/installation.md)
- [Developer guide](docs/developer-guide.md)
- [User guide](docs/user-guide.md)
- [FAQ](docs/faq.md)
- [Architecture decisions](docs/decisions)

## Contributing and security

Contributions are welcome after reading [CONTRIBUTING.md](CONTRIBUTING.md) and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Please report vulnerabilities using
the process in [SECURITY.md](SECURITY.md), not through public issues.

## License

Released under the [MIT License](LICENSE).
