[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$CandidateRoot,

    [Parameter(Mandatory = $true)]
    [string]$WorkingDirectory,

    [Parameter(Mandatory = $true)]
    [string]$FilePath,

    [Parameter(Mandatory = $true)]
    [string[]]$ArgumentList,

    [Parameter(Mandatory = $true)]
    [string]$Label,

    [Parameter(Mandatory = $true)]
    [string]$ReportDirectory,

    [ValidateRange(15, 600)]
    [int]$TimeoutSeconds = 120,

    [ValidateRange(1, 10)]
    [int]$SampleSeconds = 2,

    [ValidateRange(2, 100)]
    [int]$MaximumRelevantProcesses = 20,

    [ValidateRange(10, 60)]
    [int]$PostExitSeconds = 10
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$resolvedCandidateRoot = [System.IO.Path]::GetFullPath($CandidateRoot).TrimEnd("\")
$resolvedWorkingDirectory = [System.IO.Path]::GetFullPath($WorkingDirectory)
$resolvedReportDirectory = [System.IO.Path]::GetFullPath($ReportDirectory)
$candidatePattern = [regex]::Escape($resolvedCandidateRoot)
$currentHarnessPid = $PID
$knownProcessIds = [System.Collections.Generic.HashSet[int]]::new()
$sampleCounts = [System.Collections.Generic.List[int]]::new()
$failures = [System.Collections.Generic.List[string]]::new()
$cleanupRequired = $false
$rootProcess = $null
$startedAt = [DateTimeOffset]::UtcNow
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

New-Item -ItemType Directory -Path $resolvedReportDirectory -Force | Out-Null
$safeLabel = $Label -replace "[^A-Za-z0-9_.-]", "-"
$snapshotPath = Join-Path $resolvedReportDirectory "$safeLabel-process-tree.jsonl"
$summaryPath = Join-Path $resolvedReportDirectory "$safeLabel-summary.json"
$stdoutPath = Join-Path $resolvedReportDirectory "$safeLabel-stdout.log"
$stderrPath = Join-Path $resolvedReportDirectory "$safeLabel-stderr.log"

function Get-WindowsProcessSnapshot {
    @(Get-CimInstance -ClassName Win32_Process | ForEach-Object {
        [pscustomobject]@{
            ProcessId = [int]$_.ProcessId
            ParentProcessId = [int]$_.ParentProcessId
            Name = [string]$_.Name
            ExecutablePath = [string]$_.ExecutablePath
            CommandLine = [string]$_.CommandLine
        }
    })
}

function Test-ProductLikeProcess {
    param([Parameter(Mandatory = $true)]$Process)

    if ([int]$Process.ProcessId -eq $currentHarnessPid) {
        return $false
    }

    $name = [string]$Process.Name
    $executablePath = [string]$Process.ExecutablePath
    $commandLine = [string]$Process.CommandLine

    if ($name -match "(?i)^(p?athena|athena-core|athena-scheduler)([-_.].*)?\.exe$") {
        return $true
    }
    if ($executablePath -and $executablePath -match "(?i)^$candidatePattern(?:\\|$)") {
        return $true
    }
    if ($commandLine -match '(?i)(?:^|\s|")-m\s+athena(?:\.|\s|$)') {
        return $true
    }
    if ($commandLine -match "(?i)(?:athena-desktop|athena-local-smoke|pATHENA)") {
        return $true
    }
    return $false
}

function Update-KnownDescendants {
    param([Parameter(Mandatory = $true)][object[]]$Processes)

    $changed = $true
    while ($changed) {
        $changed = $false
        foreach ($process in $Processes) {
            $processId = [int]$process.ProcessId
            $parentProcessId = [int]$process.ParentProcessId
            if (
                -not $knownProcessIds.Contains($processId) -and
                $knownProcessIds.Contains($parentProcessId)
            ) {
                [void]$knownProcessIds.Add($processId)
                $changed = $true
            }
        }
    }
}

function Get-RelevantProcesses {
    param([Parameter(Mandatory = $true)][object[]]$Processes)

    @($Processes | Where-Object {
        $knownProcessIds.Contains([int]$_.ProcessId) -or (Test-ProductLikeProcess $_)
    })
}

function Write-ProcessSample {
    param(
        [Parameter(Mandatory = $true)][object[]]$Processes,
        [Parameter(Mandatory = $true)][string]$Phase
    )

    $payload = [ordered]@{
        candidate_sha = [string]$env:CANDIDATE_SHA
        label = $Label
        phase = $Phase
        timestamp_utc = [DateTimeOffset]::UtcNow.ToString("O")
        elapsed_seconds = [Math]::Round($stopwatch.Elapsed.TotalSeconds, 3)
        process_count = $Processes.Count
        processes = @($Processes | Sort-Object ProcessId | ForEach-Object {
            [ordered]@{
                pid = [int]$_.ProcessId
                parent_pid = [int]$_.ParentProcessId
                name = [string]$_.Name
                executable_path = [string]$_.ExecutablePath
                command_line = [string]$_.CommandLine
            }
        })
    }
    Add-Content -LiteralPath $snapshotPath -Value ($payload | ConvertTo-Json -Depth 6 -Compress)
}

function Add-Failure {
    param([Parameter(Mandatory = $true)][string]$Message)

    if (-not $failures.Contains($Message)) {
        $failures.Add($Message)
    }
}

function Test-SustainedGrowth {
    if ($sampleCounts.Count -lt 4 -or $stopwatch.Elapsed.TotalSeconds -lt 8) {
        return $false
    }

    $lastFour = @($sampleCounts | Select-Object -Last 4)
    return (
        $lastFour[0] -lt $lastFour[1] -and
        $lastFour[1] -lt $lastFour[2] -and
        $lastFour[2] -lt $lastFour[3] -and
        ($lastFour[3] - $lastFour[0]) -ge 3
    )
}

function Stop-RelevantProcesses {
    $processes = Get-WindowsProcessSnapshot
    Update-KnownDescendants $processes
    $relevant = @(Get-RelevantProcesses $processes | Sort-Object ProcessId -Descending)
    foreach ($process in $relevant) {
        $processId = [int]$process.ProcessId
        if ($processId -eq $currentHarnessPid) {
            continue
        }
        try {
            Stop-Process -Id $processId -Force -ErrorAction Stop
            $script:cleanupRequired = $true
        }
        catch [Microsoft.PowerShell.Commands.ProcessCommandException] {
            # The process may have exited between the snapshot and cleanup.
        }
    }
}

$baselineProcesses = Get-WindowsProcessSnapshot
$baselineRelevant = @(Get-RelevantProcesses $baselineProcesses)
Write-ProcessSample -Processes $baselineRelevant -Phase "before-start"
if ($baselineRelevant.Count -ne 0) {
    $baselineIds = ($baselineRelevant.ProcessId | Sort-Object) -join ", "
    throw "Unsafe baseline: product-like processes already exist (PIDs: $baselineIds)."
}

try {
    $quotedArguments = @($ArgumentList | ForEach-Object {
        if ($_ -match '[\s"]') {
            '"' + $_.Replace('"', '\"') + '"'
        }
        else {
            $_
        }
    })

    $rootProcess = Start-Process `
        -FilePath $FilePath `
        -ArgumentList $quotedArguments `
        -WorkingDirectory $resolvedWorkingDirectory `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath `
        -PassThru
    [void]$knownProcessIds.Add([int]$rootProcess.Id)

    while ($true) {
        Start-Sleep -Seconds $SampleSeconds
        $processes = Get-WindowsProcessSnapshot
        Update-KnownDescendants $processes
        $relevant = @(Get-RelevantProcesses $processes)
        Write-ProcessSample -Processes $relevant -Phase "running"
        $sampleCounts.Add($relevant.Count)

        if ($relevant.Count -ge $MaximumRelevantProcesses) {
            Add-Failure "Process safety threshold reached: $($relevant.Count) relevant processes (limit is fewer than $MaximumRelevantProcesses)."
            break
        }

        $duplicateCommands = @(
            $relevant |
                Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_.CommandLine) } |
                Group-Object { ([string]$_.CommandLine).Trim().ToLowerInvariant() } |
                Where-Object Count -ge 3
        )
        if ($duplicateCommands.Count -gt 0) {
            Add-Failure "Repeated self-recursion signature detected in three or more processes."
            break
        }

        if (Test-SustainedGrowth) {
            Add-Failure "Unbounded process growth detected across four consecutive samples."
            break
        }

        $rootProcess.Refresh()
        if ($rootProcess.HasExited) {
            break
        }
        if ($stopwatch.Elapsed.TotalSeconds -ge $TimeoutSeconds) {
            Add-Failure "Controlled process exceeded the $TimeoutSeconds second deadman timeout."
            break
        }
    }

    $rootProcess.Refresh()
    if (-not $rootProcess.HasExited) {
        Add-Failure "Root process did not exit under its own control."
    }
    elseif ($rootProcess.ExitCode -ne 0) {
        Add-Failure "Root process exited with code $($rootProcess.ExitCode)."
    }

    Start-Sleep -Seconds $PostExitSeconds
    $postExitProcesses = Get-WindowsProcessSnapshot
    Update-KnownDescendants $postExitProcesses
    $postExitRelevant = @(Get-RelevantProcesses $postExitProcesses)
    Write-ProcessSample -Processes $postExitRelevant -Phase "after-$PostExitSeconds-seconds"
    if ($postExitRelevant.Count -ne 0) {
        $postExitIds = ($postExitRelevant.ProcessId | Sort-Object) -join ", "
        Add-Failure "Product or descendant processes remained $PostExitSeconds seconds after controlled exit (PIDs: $postExitIds)."
    }
}
finally {
    if ($failures.Count -gt 0 -or ($null -ne $rootProcess -and -not $rootProcess.HasExited)) {
        Stop-RelevantProcesses
    }
    if ($cleanupRequired) {
        Add-Failure "Orphan cleanup was required; this run is UNSAFE-DIAGNOSTIC and RED."
    }

    $stopwatch.Stop()
    $summary = [ordered]@{
        candidate_sha = [string]$env:CANDIDATE_SHA
        label = $Label
        status = if ($failures.Count -eq 0) { "PASS" } else { "FAIL" }
        started_at_utc = $startedAt.ToString("O")
        duration_seconds = [Math]::Round($stopwatch.Elapsed.TotalSeconds, 3)
        root_pid = if ($null -eq $rootProcess) { $null } else { [int]$rootProcess.Id }
        root_exit_code = if ($null -eq $rootProcess -or -not $rootProcess.HasExited) { $null } else { [int]$rootProcess.ExitCode }
        maximum_relevant_processes = if ($sampleCounts.Count -eq 0) { 0 } else { ($sampleCounts | Measure-Object -Maximum).Maximum }
        post_exit_wait_seconds = $PostExitSeconds
        cleanup_required = $cleanupRequired
        failures = @($failures)
        process_samples = $snapshotPath
        stdout = $stdoutPath
        stderr = $stderrPath
    }
    Set-Content -LiteralPath $summaryPath -Value ($summary | ConvertTo-Json -Depth 6)
    Write-Output ($summary | ConvertTo-Json -Depth 6)
}

if ($failures.Count -gt 0) {
    throw ($failures -join " ")
}
