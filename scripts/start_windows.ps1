param(
    [string]$LocalRoot = "",
    [string]$LmStudioBaseUrl = "",
    [switch]$NoSync
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

if ($env:OS -ne "Windows_NT") {
    throw "This launcher is intended for Windows."
}

$uvCommand = Get-Command uv -ErrorAction SilentlyContinue
if ($null -eq $uvCommand) {
    throw "uv is not available. Run .\scripts\bootstrap_windows.ps1 first."
}

$uvVersion = (& uv --version).Trim()
if ($LASTEXITCODE -ne 0 -or $uvVersion -ne "uv 0.11.21") {
    throw "pATHENA requires uv 0.11.21. Run .\scripts\bootstrap_windows.ps1."
}

if ($LocalRoot.Trim()) {
    $env:ATHENA_LOCAL_ROOT = [System.IO.Path]::GetFullPath($LocalRoot)
}

if ($LmStudioBaseUrl.Trim()) {
    $env:ATHENA_LMSTUDIO_BASE_URL = $LmStudioBaseUrl.Trim()
}

if (-not $NoSync) {
    & uv sync --locked --extra desktop
    if ($LASTEXITCODE -ne 0) {
        throw "Locked desktop environment synchronization failed."
    }
}

Write-Host "Starting pATHENA desktop..."
if ($env:ATHENA_LOCAL_ROOT) {
    Write-Host "Runtime root: $env:ATHENA_LOCAL_ROOT"
} else {
    Write-Host "Runtime root: $env:LOCALAPPDATA\ATHENA"
}
Write-Host "LM Studio: $($env:ATHENA_LMSTUDIO_BASE_URL ?? 'http://127.0.0.1:1234')"

& uv run --locked --extra desktop athena-desktop
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    throw "pATHENA desktop exited with code $exitCode."
}
