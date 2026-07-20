# Developer Guide

## Daily workflow

1. Start from a GitHub issue with agreed acceptance criteria.
2. Create a focused branch from `main`.
3. Make the smallest coherent change.
4. Run formatting, linting, and tests locally.
5. Open a pull request that links the issue.

## Commands

| Task | Command |
| --- | --- |
| Format Python | `.\scripts\format.ps1` |
| Lint Python | `.\scripts\lint.ps1` |
| Run tests | `python -m pytest` |
| Build package | `.\scripts\build.ps1` |
| Validate documentation | `python scripts/check_docs.py` |

If Windows blocks a PowerShell script, allow scripts for the current terminal
process only, then run the command again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Source placement

- Reusable code: `src/aerobictoolkit/`
- Tests: `tests/`
- Runnable learning examples: `examples/`
- Local files produced or consumed at runtime: `data/`
- Automation and maintenance helpers: `scripts/`
- Long-lived design decisions: `docs/decisions/`

## Quality gate

Before a pull request is reviewed, it must pass Ruff and pytest. CI repeats
these checks on Python 3.12. Documentation changes must also pass the document
structure check.

## Versioning and releases

Update `pyproject.toml`, `src/aerobictoolkit/__init__.py`, and `CHANGELOG.md`
in the same release change. Release tags use `v` plus the package version, for
example `v0.2.0`. The release workflow builds the distribution and creates
GitHub release notes from the tag.
