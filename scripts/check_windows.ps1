param(
    [switch]$RequireModel,
    [switch]$SkipRestartSmoke,
    [switch]$NoSync
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$CommonScript = Join-Path $ScriptDir "windows_common.ps1"
if (-not (Test-Path -LiteralPath $CommonScript -PathType Leaf)) {
    throw "Missing Windows helper: $CommonScript"
}
. $CommonScript

if ($env:OS -ne "Windows_NT") {
    throw "This diagnostic script is intended for Windows."
}

Set-Location $RepoRoot
$loadedSettings = Import-PathenaWindowsSettings -RepoRoot $RepoRoot
if ($loadedSettings) {
    Write-Host "Loaded local Windows settings from .pathena.windows.ps1"
}

$uvCommand = Get-Command uv -ErrorAction SilentlyContinue
if ($null -eq $uvCommand) {
    throw "uv is not available. Run .\scripts\bootstrap_windows.ps1 first."
}

$uvVersion = (& uv --version).Trim()
if ($LASTEXITCODE -ne 0 -or $uvVersion -ne "uv 0.11.21") {
    throw "pATHENA requires uv 0.11.21. Run .\scripts\bootstrap_windows.ps1."
}

if (-not $NoSync) {
    Write-Host "Synchronizing locked desktop runtime..."
    & uv sync --locked --extra desktop
    if ($LASTEXITCODE -ne 0) {
        throw "Locked desktop environment synchronization failed."
    }
}

Write-Host "Running pATHENA doctor..."
$doctorArgs = @(
    "run", "--locked", "--extra", "desktop", "--no-sync", "athena-doctor"
)
if ($RequireModel) {
    $doctorArgs += "--require-model"
}
& uv @doctorArgs
if ($LASTEXITCODE -ne 0) {
    throw "pATHENA doctor failed with exit code $LASTEXITCODE."
}

if (-not $SkipRestartSmoke) {
    Write-Host "Running disposable Core/API restart smoke test..."
    & uv run --locked --extra desktop --no-sync athena-local-smoke
    if ($LASTEXITCODE -ne 0) {
        throw "pATHENA local restart smoke test failed with exit code $LASTEXITCODE."
    }
}

Write-Host "pATHENA Windows checks: PASS"
