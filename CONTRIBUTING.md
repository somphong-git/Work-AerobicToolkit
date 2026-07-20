# Contributing to Work-AerobicToolkit

Thank you for contributing. The project is in a foundation-first phase, so
clarity, small changes, and a traceable decision history matter more than
delivery speed.

## Before you start

1. Search existing issues and discussions.
2. Open or join an issue before writing a feature or making a material change.
3. Agree on scope, acceptance criteria, and ownership in that issue.
4. Create a focused branch from `main`, such as `codex/issue-42-scanner-tests`.

The working flow is: **issue → discussion → branch → commit → pull request →
merge**.

## Local setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
.\scripts\lint.ps1
python -m pytest
```

## Making a change

- Keep product logic inside `src/aerobictoolkit/`; do not put it in scripts,
  examples, or a future interface.
- Add or update tests for behavior changes.
- Format and lint before opening a pull request.
- Update documentation and `CHANGELOG.md` when the user-visible or developer
  experience changes.
- Keep commits small and imperative, for example:
  `docs: add installation guide`.

## Pull requests

Use the pull request template and link the issue it resolves. A pull request
should describe its intent, tests run, documentation impact, and any deferred
work. Do not merge changes that leave CI failing.

## Code of conduct

By participating, you agree to follow the
[Code of Conduct](CODE_OF_CONDUCT.md).
