# Change this to your routes folder path
$folderPath = "C:\Users\ALEX\Desktop\Smartscripts\smartscripts\app\teacher\routes"

# Get all Python files
$files = Get-ChildItem -Path $folderPath -Filter "*.py" -Recurse

# Extract all function definitions
$functions = foreach ($file in $files) {
    Select-String -Path $file.FullName -Pattern "^\s*def\s+(\w+)\s*\(" | ForEach-Object {
        # Extract function name from matched line
        $matches = [regex]::Match($_.Line, "^\s*def\s+(\w+)\s*\(")
        [PSCustomObject]@{
            FunctionName = $matches.Groups[1].Value
            File = $file.FullName
        }
    }
}

# Group by function name and find duplicates
$duplicates = $functions | Group-Object FunctionName | Where-Object { $_.Count -gt 1 }

if ($duplicates.Count -eq 0) {
    Write-Output "No duplicate function names found."
} else {
    Write-Output "Duplicate function names found:`n"
    foreach ($dup in $duplicates) {
        Write-Output "Function: $($dup.Name) - Occurrences: $($dup.Count)"
        foreach ($entry in $dup.Group) {
            Write-Output " - $($entry.File)"
        }
        Write-Output ""
    }
}
