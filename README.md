# Work-AerobicToolkit

Work-AerobicToolkit is an open-source, engine-first foundation for aerobic DJ
mix workflows. The same core package is intended to support future CLI,
desktop, web, API, plugin, agent, and mobile interfaces.

> **Project status:** pre-alpha. Sprint 2.2 establishes repository standards;
> BPM analysis, playlist generation, and mix rendering are deliberately not
> implemented yet.

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
