# Installation

## Requirements

- Python 3.12 or newer
- Git

## Development installation

From the repository root, create and activate a virtual environment, then
install the development extra.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### macOS and Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Verify

```bash
python -m aerobictoolkit --version
python -m pytest
```

If your shell cannot find Python, install Python 3.12+ and reopen the terminal.
The repository currently has no mandatory audio-processing dependency; those
will be introduced with the engine features that use them.
