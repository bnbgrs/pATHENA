Set-StrictMode -Version Latest

$script:PathenaPortableOutputMarkerName = ".pathena-windows-portable-output"
$script:PathenaPortableOutputMarkerValue = "pATHENA Windows Portable Output v1"

function Normalize-PathenaPackagingPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $pathRoot = [System.IO.Path]::GetPathRoot($fullPath)
    if ($fullPath.Equals($pathRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $pathRoot
    }
    return $fullPath.TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
}

function Test-PathenaPackagingPathEqual {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Left,
        [Parameter(Mandatory = $true)][string]$Right
    )

    $normalizedLeft = Normalize-PathenaPackagingPath -Path $Left
    $normalizedRight = Normalize-PathenaPackagingPath -Path $Right
    return $normalizedLeft.Equals(
        $normalizedRight,
        [System.StringComparison]::OrdinalIgnoreCase
    )
}

function Test-PathenaPackagingPathWithin {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$ParentPath
    )

    $candidate = Normalize-PathenaPackagingPath -Path $Path
    $parent = Normalize-PathenaPackagingPath -Path $ParentPath
    if ($candidate.Equals($parent, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $true
    }

    $separator = [System.IO.Path]::DirectorySeparatorChar.ToString()
    $prefix = if ($parent.EndsWith($separator, [System.StringComparison]::Ordinal)) {
        $parent
    }
    else {
        $parent + $separator
    }
    return $candidate.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)
}

function Test-PathenaPackagingReparsePointInChain {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [string]$StopBeforePath = ""
    )

    $current = Normalize-PathenaPackagingPath -Path $Path
    $stopBefore = if ([string]::IsNullOrWhiteSpace($StopBeforePath)) {
        $null
    }
    else {
        Normalize-PathenaPackagingPath -Path $StopBeforePath
    }

    while ($true) {
        if ($null -ne $stopBefore -and (Test-PathenaPackagingPathEqual -Left $current -Right $stopBefore)) {
            return $false
        }
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                return $true
            }
        }

        $parent = [System.IO.Path]::GetDirectoryName($current)
        if ([string]::IsNullOrWhiteSpace($parent)) {
            return $false
        }
        $parent = Normalize-PathenaPackagingPath -Path $parent
        if (Test-PathenaPackagingPathEqual -Left $current -Right $parent) {
            return $false
        }
        $current = $parent
    }
}

function Test-PathenaPortableOutputOwnershipMarker {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$OutputRoot
    )

    $markerPath = Join-Path $OutputRoot $script:PathenaPortableOutputMarkerName
    if (-not (Test-Path -LiteralPath $markerPath -PathType Leaf)) {
        return $false
    }

    $markerItem = Get-Item -LiteralPath $markerPath -Force
    if (($markerItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        return $false
    }

    $markerValue = (Get-Content -LiteralPath $markerPath -Raw -ErrorAction Stop).Trim()
    return $markerValue.Equals(
        $script:PathenaPortableOutputMarkerValue,
        [System.StringComparison]::Ordinal
    )
}

function Assert-PathenaPortableOutputRoot {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$OutputRoot,
        [Parameter(Mandatory = $true)][string]$DefaultOutputRoot
    )

    $repo = Normalize-PathenaPackagingPath -Path $RepoRoot
    $output = Normalize-PathenaPackagingPath -Path $OutputRoot
    $defaultOutput = Normalize-PathenaPackagingPath -Path $DefaultOutputRoot
    $filesystemRoot = Normalize-PathenaPackagingPath -Path ([System.IO.Path]::GetPathRoot($output))

    if (Test-PathenaPackagingPathEqual -Left $output -Right $filesystemRoot) {
        throw "Refusing Windows packaging OutputRoot at filesystem root '$output'."
    }

    if (Test-PathenaPackagingPathWithin -Path $repo -ParentPath $output) {
        throw "Refusing Windows packaging OutputRoot that is the repository or its ancestor: '$output'."
    }

    $insideRepo = Test-PathenaPackagingPathWithin -Path $output -ParentPath $repo
    $insideManagedSubtree = Test-PathenaPackagingPathWithin -Path $output -ParentPath $defaultOutput
    if ($insideRepo -and -not $insideManagedSubtree) {
        throw (
            "Refusing Windows packaging OutputRoot inside the repository but outside the managed " +
            "'$defaultOutput' subtree: '$output'."
        )
    }

    $stopBefore = if ($insideRepo) { $repo } else { "" }
    if (Test-PathenaPackagingReparsePointInChain -Path $output -StopBeforePath $stopBefore) {
        throw "Refusing Windows packaging OutputRoot through a junction or reparse point: '$output'."
    }

    if (Test-Path -LiteralPath $output) {
        if (-not (Test-Path -LiteralPath $output -PathType Container)) {
            throw "Refusing Windows packaging OutputRoot because the existing target is not a directory: '$output'."
        }

        if (-not (Test-PathenaPackagingPathEqual -Left $output -Right $defaultOutput) -and
            -not (Test-PathenaPortableOutputOwnershipMarker -OutputRoot $output)) {
            throw (
                "Refusing to recursively replace unowned Windows packaging OutputRoot '$output'. " +
                "Use a fresh directory or a directory created by a previous pATHENA portable build."
            )
        }
    }

    return $output
}

function Set-PathenaPortableOutputOwnershipMarker {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$OutputRoot
    )

    if (-not (Test-Path -LiteralPath $OutputRoot -PathType Container)) {
        throw "Cannot mark missing Windows packaging OutputRoot '$OutputRoot'."
    }
    $markerPath = Join-Path $OutputRoot $script:PathenaPortableOutputMarkerName
    Set-Content -LiteralPath $markerPath -Value $script:PathenaPortableOutputMarkerValue -Encoding ASCII -NoNewline
}
