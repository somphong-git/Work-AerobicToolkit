[CmdletBinding()]
param(
    [switch]$CreateTag,
    [switch]$Push
)

$ErrorActionPreference = "Stop"

if (git status --porcelain) {
    throw "Release requires a clean working tree. Commit or stash changes first."
}

$version = python -c "from aerobictoolkit import __version__; print(__version__)"
$tag = "v$version"

& "$PSScriptRoot\build.ps1"

if (-not $CreateTag) {
    Write-Host "Built release artifacts for $tag. Re-run with -CreateTag to create the Git tag."
    return
}

if (git tag --list $tag) {
    throw "Tag $tag already exists."
}

git tag --annotate $tag --message "Release $tag"

if ($Push) {
    git push origin $tag
}
