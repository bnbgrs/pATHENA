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

function Invoke-PathenaPyInstaller {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$EntryPoint,
        [Parameter(Mandatory = $true)][string]$DistPath,
        [Parameter(Mandatory = $true)][string]$WorkPath,
        [Parameter(Mandatory = $true)][string]$SpecPath
    )

    foreach ($path in @($DistPath, $WorkPath, $SpecPath)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }

    & $script:python -m PyInstaller `
        --noconfirm `
        --clean `
        --onedir `
        --windowed `
        --noupx `
        --contents-directory app_runtime `
        --name $Name `
        --paths src `
        --collect-submodules athena `
        --collect-all usearch `
        --collect-all cryptography `
        --collect-all pypdf `
        --distpath $DistPath `
        --workpath $WorkPath `
        --specpath $SpecPath `
        $EntryPoint
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed to build $Name."
    }
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
    $workerDist = Join-Path $repoRoot "build\windows-portable-worker-dist"

    foreach ($path in @($resolvedOutput, $workRoot, $specRoot, $workerDist)) {
        if (Test-Path -LiteralPath $path) {
            Remove-Item -LiteralPath $path -Recurse -Force
        }
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }

    Invoke-PathenaPyInstaller `
        -Name "pATHENA" `
        -EntryPoint "src\athena\desktop\packaged_app.py" `
        -DistPath $resolvedOutput `
        -WorkPath (Join-Path $workRoot "desktop") `
        -SpecPath (Join-Path $specRoot "desktop")

    Invoke-PathenaPyInstaller `
        -Name "pATHENA-Worker" `
        -EntryPoint "src\athena\desktop\packaged_worker.py" `
        -DistPath $workerDist `
        -WorkPath (Join-Path $workRoot "worker") `
        -SpecPath (Join-Path $specRoot "worker")

    $packageRoot = Join-Path $resolvedOutput "pATHENA"
    $executable = Join-Path $packageRoot "pATHENA.exe"
    $workerSourceRoot = Join-Path $workerDist "pATHENA-Worker"
    $workerSource = Join-Path $workerSourceRoot "pATHENA-Worker.exe"
    $workerRuntime = Join-Path $workerSourceRoot "app_runtime"
    $workerTarget = Join-Path $packageRoot "pATHENA-Worker.exe"
    $runtime = Join-Path $packageRoot "app_runtime"
    $hardwareCheck = Join-Path $packageRoot "CHECK_HARDWARE.cmd"

    if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
        throw "pATHENA.exe was not produced."
    }
    if (-not (Test-Path -LiteralPath $workerSource -PathType Leaf)) {
        throw "pATHENA-Worker.exe was not produced."
    }
    if (-not (Test-Path -LiteralPath $runtime -PathType Container)) {
        throw "The pATHENA onedir runtime directory was not produced."
    }
    if (-not (Test-Path -LiteralPath $workerRuntime -PathType Container)) {
        throw "The pATHENA worker runtime directory was not produced."
    }

    # Both analyses collect the same ATHENA module tree. Merge any worker-specific
    # binary/runtime additions into the desktop onedir, then keep only the hidden
    # worker executable beside pATHENA.exe.
    Copy-Item -LiteralPath $workerSource -Destination $workerTarget -Force
    Copy-Item -Path (Join-Path $workerRuntime "*") -Destination $runtime -Recurse -Force
    Remove-Item -LiteralPath $workerDist -Recurse -Force

    if (-not (Test-Path -LiteralPath $workerTarget -PathType Leaf)) {
        throw "The assembled package is missing pATHENA-Worker.exe."
    }

    @"
@echo off
setlocal
cd /d "%~dp0"
"%~dp0pATHENA-Worker.exe" -m athena.hardware_acceptance --output "%~dp0hardware-acceptance.json" %*
set "PATHENA_HW_EXIT=%ERRORLEVEL%"
echo.
echo Hardware acceptance report: %~dp0hardware-acceptance.json
if "%PATHENA_HW_EXIT%"=="0" (
  echo pATHENA target hardware acceptance: PASS
) else (
  echo pATHENA target hardware acceptance: FAIL ^(exit %PATHENA_HW_EXIT%^)
)
exit /b %PATHENA_HW_EXIT%
"@ | Set-Content -LiteralPath $hardwareCheck -Encoding ASCII

    if (-not (Test-Path -LiteralPath $hardwareCheck -PathType Leaf)) {
        throw "The assembled package is missing CHECK_HARDWARE.cmd."
    }

    @"
pATHENA Windows Portable
========================

Start:
  pATHENA.exe

Target workstation acceptance:
  CHECK_HARDWARE.cmd

The hardware check requires the actual Windows workstation. It verifies the expected
AMD Radeon RX 7900 XTX through Windows CIM, requires an already-loaded local LLM in
LM Studio, performs one real short inference with reasoning disabled, and writes
hardware-acceptance.json beside the package. Optional arguments are passed through;
for example CHECK_HARDWARE.cmd --model-id <loaded-model-id>.

Keep together:
  pATHENA.exe
  pATHENA-Worker.exe
  CHECK_HARDWARE.cmd
  app_runtime\

pATHENA.exe is the no-console desktop. pATHENA-Worker.exe is a no-console internal
process host for Core, Scheduler lanes, JOBS receipts, and the explicit hardware
acceptance probe. The desktop binds all sys.executable child launches to that sibling
before normal application startup, and the worker accepts only the explicit internal
'-m' module roles used by pATHENA. Unknown module dispatches fail closed instead of
reopening the desktop.
"@ | Set-Content -LiteralPath (Join-Path $packageRoot "START_HERE.txt") -Encoding UTF8

    Write-Output $executable
}
finally {
    Pop-Location
}
