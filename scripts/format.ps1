[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

python -m ruff format src tests examples scripts
