Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-PathenaWindowsSettingsPath {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)
    return (Join-Path $RepoRoot ".pathena.windows.ps1")
}

function Resolve-PathenaDefaultLocalRoot {
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

function Resolve-PathenaEffectiveLocalRoot {
    if ($env:ATHENA_LOCAL_ROOT -and $env:ATHENA_LOCAL_ROOT.Trim()) {
        return [System.IO.Path]::GetFullPath($env:ATHENA_LOCAL_ROOT.Trim())
    }
    return Resolve-PathenaDefaultLocalRoot
}

function Assert-PathenaRuntimeRootOutsideRepository {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$RuntimeRoot
    )

    $trimChars = [char[]]@('\', '/')
    $repo = [System.IO.Path]::GetFullPath($RepoRoot).TrimEnd($trimChars)
    $runtime = [System.IO.Path]::GetFullPath($RuntimeRoot).TrimEnd($trimChars)
    $comparison = [System.StringComparison]::OrdinalIgnoreCase
    $repoPrefix = $repo + [System.IO.Path]::DirectorySeparatorChar

    if ($runtime.Equals($repo, $comparison) -or $runtime.StartsWith($repoPrefix, $comparison)) {
        throw "pATHENA runtime root must be outside the repository: $runtime. Choose -LocalRoot in AppData or a separate data directory."
    }
    return $runtime
}

function Assert-PathenaLocalRootReady {
    param([string]$RepoRoot = "")

    $root = Resolve-PathenaEffectiveLocalRoot
    if ($RepoRoot.Trim()) {
        $root = Assert-PathenaRuntimeRootOutsideRepository -RepoRoot $RepoRoot -RuntimeRoot $root
    }
    try {
        [System.IO.Directory]::CreateDirectory($root) | Out-Null
        $probe = Join-Path $root (".pathena-write-probe-" + [Guid]::NewGuid().ToString("N") + ".tmp")
        [System.IO.File]::WriteAllText($probe, "pATHENA write probe", [System.Text.UTF8Encoding]::new($false))
        Remove-Item -LiteralPath $probe -Force
    } catch {
        throw "pATHENA runtime root is not writable: $root. Choose a writable -LocalRoot. $($_.Exception.Message)"
    }
    return $root
}

function Get-PathenaUvVersion {
    $command = Get-Command uv -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        return $null
    }

    try {
        $output = @(& uv --version 2>$null)
        $exitCode = $LASTEXITCODE
    } catch {
        return $null
    }

    if ($exitCode -ne 0 -or $output.Count -eq 0) {
        return $null
    }

    $version = ($output -join [Environment]::NewLine).Trim()
    if (-not $version) {
        return $null
    }
    return $version
}

function ConvertFrom-PathenaSettingsLiteral {
    param(
        [Parameter(Mandatory = $true)][string]$Literal,
        [Parameter(Mandatory = $true)][string]$SettingsPath,
        [Parameter(Mandatory = $true)][int]$LineNumber
    )

    if ($Literal.Length -lt 2 -or $Literal[0] -ne "'" -or $Literal[$Literal.Length - 1] -ne "'") {
        throw "Invalid pATHENA Windows settings value at ${SettingsPath}:$LineNumber. Values must be single-quoted literals."
    }

    $inner = $Literal.Substring(1, $Literal.Length - 2)
    $builder = [System.Text.StringBuilder]::new()
    for ($index = 0; $index -lt $inner.Length; $index++) {
        $character = $inner[$index]
        if ($character -eq "'") {
            if ($index + 1 -ge $inner.Length -or $inner[$index + 1] -ne "'") {
                throw "Invalid pATHENA Windows settings escape at ${SettingsPath}:$LineNumber."
            }
            [void]$builder.Append("'")
            $index++
            continue
        }
        [void]$builder.Append($character)
    }
    return $builder.ToString()
}

function Import-PathenaWindowsSettings {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)

    $settingsPath = Get-PathenaWindowsSettingsPath -RepoRoot $RepoRoot
    if (-not (Test-Path -LiteralPath $settingsPath -PathType Leaf)) {
        return $false
    }

    $allowedSettings = @{
        '$env:ATHENA_LOCAL_ROOT' = 'ATHENA_LOCAL_ROOT'
        '$env:ATHENA_LMSTUDIO_BASE_URL' = 'ATHENA_LMSTUDIO_BASE_URL'
    }
    $seenSettings = @{}
    $lineNumber = 0

    foreach ($line in [System.IO.File]::ReadAllLines($settingsPath)) {
        $lineNumber++
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith('#')) {
            continue
        }

        $separatorIndex = $trimmed.IndexOf('=')
        if ($separatorIndex -le 0) {
            throw "Invalid pATHENA Windows settings syntax at ${settingsPath}:$lineNumber."
        }

        $left = $trimmed.Substring(0, $separatorIndex).Trim()
        $right = $trimmed.Substring($separatorIndex + 1).Trim()
        if (-not $allowedSettings.ContainsKey($left)) {
            throw "Unsupported pATHENA Windows setting at ${settingsPath}:$lineNumber."
        }

        $environmentName = $allowedSettings[$left]
        if ($seenSettings.ContainsKey($environmentName)) {
            throw "Duplicate pATHENA Windows setting '$environmentName' at ${settingsPath}:$lineNumber."
        }

        $value = ConvertFrom-PathenaSettingsLiteral `
            -Literal $right `
            -SettingsPath $settingsPath `
            -LineNumber $lineNumber
        Set-Item -Path "Env:$environmentName" -Value $value
        $seenSettings[$environmentName] = $true
    }

    return $true
}

function ConvertTo-PowerShellSingleQuotedLiteral {
    param([Parameter(Mandatory = $true)][string]$Value)
    return "'" + $Value.Replace("'", "''") + "'"
}

function Save-PathenaWindowsSettings {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [string]$LocalRoot = "",
        [string]$LmStudioBaseUrl = ""
    )

    $settingsPath = Get-PathenaWindowsSettingsPath -RepoRoot $RepoRoot
    $lines = @(
        "# Local pATHENA Windows settings. Generated by bootstrap_windows.ps1.",
        "# Data-only file: windows_common.ps1 parses this strictly and never executes it."
    )

    if ($LocalRoot.Trim()) {
        $literal = ConvertTo-PowerShellSingleQuotedLiteral -Value $LocalRoot.Trim()
        $lines += "`$env:ATHENA_LOCAL_ROOT = $literal"
    }
    if ($LmStudioBaseUrl.Trim()) {
        $literal = ConvertTo-PowerShellSingleQuotedLiteral -Value $LmStudioBaseUrl.Trim()
        $lines += "`$env:ATHENA_LMSTUDIO_BASE_URL = $literal"
    }

    if ($lines.Count -eq 2) {
        if (Test-Path -LiteralPath $settingsPath) {
            Remove-Item -LiteralPath $settingsPath -Force
        }
        return
    }

    $content = ($lines -join [Environment]::NewLine) + [Environment]::NewLine
    [System.IO.File]::WriteAllText($settingsPath, $content, [System.Text.UTF8Encoding]::new($false))
}
