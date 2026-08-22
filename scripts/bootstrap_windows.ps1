param(
    [string]$LocalRoot = "",
    [switch]$SkipSmokeTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ExpectedUvVersion = "0.11.21"
$ExpectedPython = "3.12"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "=== $Message ==="
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE: $FilePath $($Arguments -join ' ')"
    }
}

function Resolve-DefaultLocalRoot {
    $localAppData = [Environment]::GetFolderPath("LocalApplicationData")
    if ($localAppData) {
        return (Join-Path $localAppData "ATHENA")
    }
    if ($env:LOCALAPPDATA) {
        return (Join-Path $env:LOCALAPPDATA "ATHENA")
    }
    if ($env:USERPROFILE) {
        return (Join-Path $env:USERPROFILE "AppData\Local\ATHENA")
    }
    throw "Windows local application-data directory could not be resolved. Pass -LocalRoot explicitly."
}

if ($env:OS -ne "Windows_NT") {
    throw "This bootstrap script is intended for Windows."
}

Set-Location $RepoRoot
Write-Host "pATHENA repository: $RepoRoot"

Write-Step "Resolve uv $ExpectedUvVersion"
$uvCommand = Get-Command uv -ErrorAction SilentlyContinue
if ($null -eq $uvCommand) {
    Write-Host "uv is not installed. Installing the pinned version from astral.sh..."
    $installer = Invoke-RestMethod "https://astral.sh/uv/$ExpectedUvVersion/install.ps1"
    Invoke-Expression $installer

    $candidateBins = @(
        (Join-Path $HOME ".local\bin"),
        (Join-Path $env:USERPROFILE ".local\bin")
    ) | Select-Object -Unique
    foreach ($candidate in $candidateBins) {
        if ((Test-Path $candidate) -and -not (($env:PATH -split ';') -contains $candidate)) {
            $env:PATH = "$candidate;$env:PATH"
        }
    }
    $uvCommand = Get-Command uv -ErrorAction SilentlyContinue
}

if ($null -eq $uvCommand) {
    throw "uv installation completed but 'uv' is still not available on PATH. Restart PowerShell and rerun this script."
}

$uvVersionOutput = (& uv --version).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Unable to read uv version."
}
if ($uvVersionOutput -ne "uv $ExpectedUvVersion") {
    throw "pATHENA requires uv $ExpectedUvVersion, but found '$uvVersionOutput'."
}
Write-Host "Using $uvVersionOutput"

Write-Step "Install Python $ExpectedPython"
Invoke-Checked uv python install $ExpectedPython

Write-Step "Configure local runtime root"
if ($LocalRoot.Trim()) {
    $resolvedLocalRoot = [System.IO.Path]::GetFullPath($LocalRoot)
    $env:ATHENA_LOCAL_ROOT = $resolvedLocalRoot
    Write-Host "ATHENA_LOCAL_ROOT=$resolvedLocalRoot"
} elseif ($env:ATHENA_LOCAL_ROOT) {
    Write-Host "ATHENA_LOCAL_ROOT=$env:ATHENA_LOCAL_ROOT"
} else {
    $defaultRoot = Resolve-DefaultLocalRoot
    Write-Host "ATHENA_LOCAL_ROOT is not overridden. pATHENA will use: $defaultRoot"
}

Write-Step "Synchronize locked pATHENA runtime"
Invoke-Checked uv sync --locked --extra desktop

Write-Step "Verify installed interpreter and package"
Invoke-Checked uv run --locked --extra desktop python -c "import sys; import athena; assert sys.version_info[:2] == (3, 12); print(sys.executable); print('athena import: OK')"

if (-not $SkipSmokeTest) {
    Write-Step "Run pATHENA local doctor"
    Invoke-Checked uv run --locked --extra desktop athena-doctor

    Write-Step "Run disposable Core/API restart smoke test"
    Invoke-Checked uv run --locked --extra desktop athena-local-smoke
}

Write-Step "Bootstrap complete"
Write-Host "Core/runtime bootstrap and restart checks succeeded. LM Studio may still be offline; athena-doctor reports that separately."
Write-Host ""
Write-Host "Start the desktop UI with:"
Write-Host "  .\scripts\start_windows.ps1"
Write-Host ""
Write-Host "Check LM Studio with:"
Write-Host "  uv run --locked --extra desktop athena model status"
Write-Host "  uv run --locked --extra desktop athena model list"
