[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

python -m ruff check src tests examples scripts
python -m ruff format --check src tests examples scripts
