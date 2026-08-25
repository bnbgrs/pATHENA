[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PackageRoot,
    [Parameter(Mandatory = $true)][string]$ReportDirectory,
    [ValidateRange(8, 60)][int]$ObserveSeconds = 16,
    [ValidateRange(1, 5)][int]$SampleSeconds = 2,
    [ValidateRange(6, 30)][int]$MaximumProcesses = 12
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$package = [System.IO.Path]::GetFullPath($PackageRoot).TrimEnd("\")
$report = [System.IO.Path]::GetFullPath($ReportDirectory)
$desktopExe = Join-Path $package "pATHENA.exe"
$workerExe = Join-Path $package "pATHENA-Worker.exe"
$runtime = Join-Path $package "app_runtime"
foreach ($required in @($desktopExe, $workerExe)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Packaged smoke missing required executable: $required"
    }
}
if (-not (Test-Path -LiteralPath $runtime -PathType Container)) {
    throw "Packaged smoke missing app_runtime directory."
}

New-Item -ItemType Directory -Path $report -Force | Out-Null
$runtimeRoot = Join-Path $report "packaged-runtime"
New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null
$env:ATHENA_LOCAL_ROOT = $runtimeRoot
$env:QT_QPA_PLATFORM = "offscreen"

$samplesPath = Join-Path $report "packaged-process-tree.jsonl"
$summaryPath = Join-Path $report "packaged-smoke-summary.json"
$knownIds = [System.Collections.Generic.HashSet[int]]::new()
$root = $null
$failures = [System.Collections.Generic.List[string]]::new()
$observedCommands = [System.Collections.Generic.List[string]]::new()
$maximumObserved = 0
$started = [DateTimeOffset]::UtcNow

function Snapshot-Processes {
    @(Get-CimInstance Win32_Process | ForEach-Object {
        [pscustomobject]@{
            ProcessId = [int]$_.ProcessId
            ParentProcessId = [int]$_.ParentProcessId
            Name = [string]$_.Name
            ExecutablePath = [string]$_.ExecutablePath
            CommandLine = [string]$_.CommandLine
        }
    })
}

function Expand-Descendants([object[]]$Processes) {
    $changed = $true
    while ($changed) {
        $changed = $false
        foreach ($process in $Processes) {
            if (
                -not $knownIds.Contains([int]$process.ProcessId) -and
                $knownIds.Contains([int]$process.ParentProcessId)
            ) {
                [void]$knownIds.Add([int]$process.ProcessId)
                $changed = $true
            }
        }
    }
}

function Relevant([object[]]$Processes) {
    @($Processes | Where-Object { $knownIds.Contains([int]$_.ProcessId) })
}

function Add-Failure([string]$Message) {
    if (-not $failures.Contains($Message)) {
        $failures.Add($Message)
    }
}

function Stop-Tree {
    $processes = Snapshot-Processes
    Expand-Descendants $processes
    $targets = @(Relevant $processes | Sort-Object ProcessId -Descending)
    foreach ($process in $targets) {
        try {
            Stop-Process -Id ([int]$process.ProcessId) -Force -ErrorAction Stop
        }
        catch [Microsoft.PowerShell.Commands.ProcessCommandException] {
            # The process may have exited between snapshot and cleanup.
        }
    }
}

$baseline = @(Snapshot-Processes | Where-Object {
    ([string]$_.ExecutablePath).StartsWith($package, [System.StringComparison]::OrdinalIgnoreCase)
})
if ($baseline.Count -ne 0) {
    throw "Packaged smoke baseline already contains pATHENA package processes."
}

try {
    $root = Start-Process -FilePath $desktopExe -WorkingDirectory $package -PassThru
    [void]$knownIds.Add([int]$root.Id)

    $deadline = [DateTimeOffset]::UtcNow.AddSeconds($ObserveSeconds)
    while ([DateTimeOffset]::UtcNow -lt $deadline) {
        Start-Sleep -Seconds $SampleSeconds
        $processes = Snapshot-Processes
        Expand-Descendants $processes
        $relevant = @(Relevant $processes)
        if ($relevant.Count -gt $maximumObserved) {
            $maximumObserved = $relevant.Count
        }
        foreach ($process in $relevant) {
            $command = ([string]$process.CommandLine).Trim()
            if ($command -and -not $observedCommands.Contains($command)) {
                $observedCommands.Add($command)
            }
        }
        [ordered]@{
            timestamp_utc = [DateTimeOffset]::UtcNow.ToString("O")
            count = $relevant.Count
            processes = @($relevant | Sort-Object ProcessId | ForEach-Object {
                [ordered]@{
                    pid = [int]$_.ProcessId
                    parent_pid = [int]$_.ParentProcessId
                    name = [string]$_.Name
                    executable = [string]$_.ExecutablePath
                    command = [string]$_.CommandLine
                }
            })
        } | ConvertTo-Json -Depth 5 -Compress | Add-Content -LiteralPath $samplesPath

        if ($relevant.Count -ge $MaximumProcesses) {
            Add-Failure "Packaged process tree reached unsafe size $($relevant.Count)."
            break
        }
        $root.Refresh()
        if ($root.HasExited) {
            Add-Failure "Packaged desktop exited during cold-start observation with code $($root.ExitCode)."
            break
        }

        $desktopDescendants = @($relevant | Where-Object {
            [int]$_.ProcessId -ne [int]$root.Id -and
            [System.IO.Path]::GetFullPath([string]$_.ExecutablePath) -eq [System.IO.Path]::GetFullPath($desktopExe)
        })
        if ($desktopDescendants.Count -ne 0) {
            Add-Failure "Desktop self-recursion detected: a descendant launched pATHENA.exe instead of pATHENA-Worker.exe."
            break
        }
    }

    $commands = $observedCommands -join "`n"
    if ($commands -notmatch '(?i)-m\s+athena\.api\.process') {
        Add-Failure "Packaged Core worker command was not observed."
    }
    if ($commands -notmatch '(?i)-m\s+athena\s+job\s+scheduler-run.*--lane\s+supervisor') {
        Add-Failure "Packaged scheduler supervisor command was not observed."
    }
    if ($commands -notmatch '(?i)--lane\s+control') {
        Add-Failure "Packaged scheduler control lane was not observed."
    }
    if ($commands -notmatch '(?i)--lane\s+provider') {
        Add-Failure "Packaged scheduler provider lane was not observed."
    }
}
finally {
    if ($null -ne $root) {
        Stop-Tree
    }
    Start-Sleep -Seconds 3
    $remaining = @(Snapshot-Processes | Where-Object {
        ([string]$_.ExecutablePath).StartsWith($package, [System.StringComparison]::OrdinalIgnoreCase)
    })
    if ($remaining.Count -ne 0) {
        Add-Failure "Packaged processes remained after controlled tree shutdown."
        foreach ($process in $remaining) {
            Stop-Process -Id ([int]$process.ProcessId) -Force -ErrorAction SilentlyContinue
        }
    }

    $summary = [ordered]@{
        candidate_sha = [string]$env:CANDIDATE_SHA
        status = if ($failures.Count -eq 0) { "PASS" } else { "FAIL" }
        started_at_utc = $started.ToString("O")
        observed_seconds = $ObserveSeconds
        maximum_processes = $maximumObserved
        commands = @($observedCommands)
        failures = @($failures)
    }
    Set-Content -LiteralPath $summaryPath -Value ($summary | ConvertTo-Json -Depth 5)
    Write-Output ($summary | ConvertTo-Json -Depth 5)
}

if ($failures.Count -ne 0) {
    throw ($failures -join " ")
}
