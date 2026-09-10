[CmdletBinding()]
param(
    [string]$OutputRoot = "",
    [switch]$ValidateOutputRootOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not $IsWindows) {
    throw "pATHENA Windows packaging must run on Windows."
}

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$defaultOutputRoot = [System.IO.Path]::GetFullPath((Join-Path $repoRoot "dist\windows-portable"))
$packageOutputMarkerName = ".pathena-windows-package-root"
$packageOutputMarkerContent = "pATHENA Windows portable package output v1"
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"

function Get-PathenaComparablePath {
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $rootPath = [System.IO.Path]::GetPathRoot($fullPath)
    $trimChars = [char[]]@('\', '/')
    if (
        $null -ne $rootPath -and
        [string]::Equals(
            $fullPath.TrimEnd($trimChars),
            $rootPath.TrimEnd($trimChars),
            [System.StringComparison]::OrdinalIgnoreCase
        )
    ) {
        return $rootPath
    }
    return $fullPath.TrimEnd($trimChars)
}

function Test-PathenaPathEqualOrInside {
    param(
        [Parameter(Mandatory = $true)][string]$Candidate,
        [Parameter(Mandatory = $true)][string]$Parent
    )

    $candidatePath = Get-PathenaComparablePath -Path $Candidate
    $parentPath = Get-PathenaComparablePath -Path $Parent
    if ([string]::Equals($candidatePath, $parentPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $true
    }
    $trimChars = [char[]]@('\', '/')
    $prefix = $parentPath.TrimEnd($trimChars) + [System.IO.Path]::DirectorySeparatorChar
    return $candidatePath.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)
}

function Assert-PathenaPackagingOutputBoundary {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$OutputRoot,
        [Parameter(Mandatory = $true)][string]$ControlledRoot
    )

    $resolvedOutput = [System.IO.Path]::GetFullPath($OutputRoot)
    $volumeRoot = [System.IO.Path]::GetPathRoot($resolvedOutput)
    $comparableOutput = Get-PathenaComparablePath -Path $resolvedOutput
    $comparableVolume = Get-PathenaComparablePath -Path $volumeRoot

    if ([string]::Equals($comparableOutput, $comparableVolume, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing Windows package output at filesystem root: $resolvedOutput"
    }
    if (Test-PathenaPathEqualOrInside -Candidate $RepoRoot -Parent $resolvedOutput) {
        throw "Refusing Windows package output that contains the repository checkout: $resolvedOutput"
    }
    if (
        (Test-PathenaPathEqualOrInside -Candidate $resolvedOutput -Parent $RepoRoot) -and
        -not (Test-PathenaPathEqualOrInside -Candidate $resolvedOutput -Parent $ControlledRoot)
    ) {
        throw "Refusing Windows package output inside the repository outside dist\windows-portable: $resolvedOutput"
    }
    return $resolvedOutput
}

function Assert-PathenaPackagingPathHasNoReparseAncestor {
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )

    $probe = [System.IO.Path]::GetFullPath($Path)
    while (-not (Test-Path -LiteralPath $probe)) {
        $parent = [System.IO.Directory]::GetParent($probe)
        if ($null -eq $parent) {
            return
        }
        $probe = $parent.FullName
    }

    while ($true) {
        $item = Get-Item -LiteralPath $probe -Force
        if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Refusing Windows package output through a reparse-point path: $($item.FullName)"
        }
        $parent = [System.IO.Directory]::GetParent($item.FullName)
        if ($null -eq $parent) {
            return
        }
        $probe = $parent.FullName
    }
}

function Initialize-PathenaPackagingOutputRoot {
    param(
        [Parameter(Mandatory = $true)][string]$OutputRoot,
        [Parameter(Mandatory = $true)][string]$ControlledRoot,
        [Parameter(Mandatory = $true)][string]$MarkerName,
        [Parameter(Mandatory = $true)][string]$MarkerContent
    )

    $isControlled = Test-PathenaPathEqualOrInside -Candidate $OutputRoot -Parent $ControlledRoot
    $markerPath = Join-Path $OutputRoot $MarkerName

    if (Test-Path -LiteralPath $OutputRoot) {
        if (-not (Test-Path -LiteralPath $OutputRoot -PathType Container)) {
            throw "Windows package output must be a directory: $OutputRoot"
        }
        if (Test-Path -LiteralPath $markerPath) {
            if (-not (Test-Path -LiteralPath $markerPath -PathType Leaf)) {
                throw "Windows package output ownership marker is not a file: $markerPath"
            }
            $existingMarker = (Get-Content -LiteralPath $markerPath -Raw).Trim()
            if ($existingMarker -ne $MarkerContent) {
                throw "Windows package output ownership marker has unexpected content: $markerPath"
            }
            return
        }
        if (-not $isControlled) {
            $existingEntries = @(Get-ChildItem -LiteralPath $OutputRoot -Force)
            if ($existingEntries.Count -ne 0) {
                throw "Refusing non-empty custom Windows package output without pATHENA ownership marker: $OutputRoot"
            }
        }
    }
    else {
        New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
    }

    Set-Content -LiteralPath $markerPath -Value $MarkerContent -Encoding ASCII
}

function Remove-PathenaGeneratedDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Refusing recursive cleanup of reparse-point package directory: $($item.FullName)"
    }
    Remove-Item -LiteralPath $Path -Recurse -Force
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

$resolvedOutput = if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $defaultOutputRoot
}
else {
    [System.IO.Path]::GetFullPath($OutputRoot)
}
$resolvedOutput = Assert-PathenaPackagingOutputBoundary `
    -RepoRoot $repoRoot `
    -OutputRoot $resolvedOutput `
    -ControlledRoot $defaultOutputRoot
Assert-PathenaPackagingPathHasNoReparseAncestor -Path $resolvedOutput
Initialize-PathenaPackagingOutputRoot `
    -OutputRoot $resolvedOutput `
    -ControlledRoot $defaultOutputRoot `
    -MarkerName $packageOutputMarkerName `
    -MarkerContent $packageOutputMarkerContent

if ($ValidateOutputRootOnly) {
    Write-Output $resolvedOutput
    exit 0
}

$uv = Get-Command uv -ErrorAction SilentlyContinue
if ($null -eq $uv) {
    throw "uv is required to build the supported pATHENA Windows package."
}

$workRoot = Join-Path $repoRoot "build\windows-portable"
$specRoot = Join-Path $repoRoot "build\windows-portable-spec"
$workerDist = Join-Path $repoRoot "build\windows-portable-worker-dist"
$packageRoot = Join-Path $resolvedOutput "pATHENA"

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

    foreach ($path in @($workRoot, $specRoot, $workerDist)) {
        Remove-PathenaGeneratedDirectory -Path $path
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
    Remove-PathenaGeneratedDirectory -Path $packageRoot

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
    Remove-PathenaGeneratedDirectory -Path $workerDist

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
