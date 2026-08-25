[CmdletBinding()]
param(
    [string]$OutputRoot = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not $IsWindows) {
    throw "pATHENA Windows packaging must run on Windows."
}

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$uv = Get-Command uv -ErrorAction SilentlyContinue
if ($null -eq $uv) {
    throw "uv is required to build the supported pATHENA Windows package."
}

Push-Location $repoRoot
try {
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        & $uv.Source sync --locked --extra desktop
        if ($LASTEXITCODE -ne 0) {
            throw "Locked pATHENA desktop environment creation failed."
        }
    }

    # PyInstaller is a build-only dependency. Pin it exactly so the package format is
    # reproducible without changing the product runtime dependency lock.
    & $uv.Source pip install --python $python "pyinstaller==6.15.0"
    if ($LASTEXITCODE -ne 0) {
        throw "Pinned PyInstaller installation failed."
    }

    $resolvedOutput = if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
        Join-Path $repoRoot "dist\windows-portable"
    }
    else {
        [System.IO.Path]::GetFullPath($OutputRoot)
    }
    $workRoot = Join-Path $repoRoot "build\windows-portable"
    $specRoot = Join-Path $repoRoot "build\windows-portable-spec"

    foreach ($path in @($resolvedOutput, $workRoot, $specRoot)) {
        if (Test-Path -LiteralPath $path) {
            Remove-Item -LiteralPath $path -Recurse -Force
        }
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }

    & $python -m PyInstaller `
        --noconfirm `
        --clean `
        --onedir `
        --windowed `
        --noupx `
        --contents-directory app_runtime `
        --name pATHENA `
        --paths src `
        --collect-submodules athena `
        --collect-all usearch `
        --collect-all cryptography `
        --collect-all pypdf `
        --distpath $resolvedOutput `
        --workpath $workRoot `
        --specpath $specRoot `
        src\athena\desktop\packaged_app.py
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed to build pATHENA."
    }

    $packageRoot = Join-Path $resolvedOutput "pATHENA"
    $executable = Join-Path $packageRoot "pATHENA.exe"
    $runtime = Join-Path $packageRoot "app_runtime"
    if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
        throw "pATHENA.exe was not produced."
    }
    if (-not (Test-Path -LiteralPath $runtime -PathType Container)) {
        throw "The pATHENA onedir runtime directory was not produced."
    }

    @"
pATHENA Windows Portable
========================

Start pATHENA.exe from this directory and keep app_runtime beside it.

This package uses one guarded executable for the desktop and its owned internal
process roles. Internal '-m athena...' launches are dispatched explicitly; unknown
module dispatches fail closed instead of reopening the desktop.
"@ | Set-Content -LiteralPath (Join-Path $packageRoot "START_HERE.txt") -Encoding UTF8

    Write-Output $executable
}
finally {
    Pop-Location
}
