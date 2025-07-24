# Check-Rollback.ps1

Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    $filePath = $_.FullName
    $lines = Get-Content $filePath
    $insideTryBlock = $false
    $foundCommit = $false
    $rollbackInExcept = $false

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = [string]$lines[$i].Trim()

        if ($line -match "^try\s*:$") {
            $insideTryBlock = $true
            $foundCommit = $false
            $rollbackInExcept = $false
        }

        if ($insideTryBlock -and $line -match "db\.session\.commit\(\)") {
            $foundCommit = $true
        }

        if ($insideTryBlock -and $line -match "^except\s") {
            $j = $i
            while ($j -lt $lines.Count -and $lines[$j] -match "^\s") {
                if ($lines[$j] -match "db\.session\.rollback\(\)") {
                    $rollbackInExcept = $true
                    break
                }
                $j++
            }
        }

        if ($insideTryBlock -and $line -eq "") {
            if ($foundCommit -and -not $rollbackInExcept) {
                Write-Host "⚠️ Missing rollback in: $filePath at approx. line $i"
            }
            $insideTryBlock = $false
        }
    }
}
