param(
    [string]$LocalRoot = "",
    [string]$LmStudioBaseUrl = "",
    [switch]$NoSync,
    [switch]$SkipPreflight
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

Set-Location $RepoRoot

if ($env:OS -ne "Windows_NT") {
    throw "This launcher is intended for Windows."
}

$loadedSettings = Import-PathenaWindowsSettings -RepoRoot $RepoRoot
if ($loadedSettings) {
    Write-Host "Loaded local Windows settings from .pathena.windows.ps1"
}

$uvVersion = Get-PathenaUvVersion
if ($uvVersion -ne "uv 0.11.21") {
    throw "pATHENA requires executable uv 0.11.21. Run .\scripts\bootstrap_windows.ps1."
}

if ($LocalRoot.Trim()) {
    $env:ATHENA_LOCAL_ROOT = [System.IO.Path]::GetFullPath($LocalRoot)
}

if ($LmStudioBaseUrl.Trim()) {
    $env:ATHENA_LMSTUDIO_BASE_URL = $LmStudioBaseUrl.Trim()
}

$runtimeRoot = Assert-PathenaLocalRootReady -RepoRoot $RepoRoot
Write-Host "Runtime root ready: $runtimeRoot"

if (-not $NoSync) {
    & uv sync --locked --extra desktop
    if ($LASTEXITCODE -ne 0) {
        throw "Locked desktop environment synchronization failed."
    }
}

if (-not $SkipPreflight) {
    Write-Host "Running local runtime preflight..."
    & uv run --locked --extra desktop --no-sync athena-doctor --no-startup-smoke
    if ($LASTEXITCODE -ne 0) {
        throw "pATHENA preflight failed. Resolve the [FAIL] diagnostics above before starting the desktop."
    }
}

Write-Host "Starting pATHENA desktop..."
Write-Host "Runtime root: $runtimeRoot"
if ($env:ATHENA_LMSTUDIO_BASE_URL) {
    Write-Host "LM Studio: $env:ATHENA_LMSTUDIO_BASE_URL"
} else {
    Write-Host "LM Studio: http://127.0.0.1:1234"
}

& uv run --locked --extra desktop --no-sync athena-desktop
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    throw "pATHENA desktop exited with code $exitCode."
}
