# Verify All Backend Files
Write-Host "🔍 Verifying All Backend Files" -ForegroundColor Green

# Check for common syntax issues in Python files
$pythonFiles = Get-ChildItem -Path "backend" -Recurse -Filter "*.py"

foreach ($file in $pythonFiles) {
    Write-Host "Checking: $($file.FullName)" -ForegroundColor Gray
    
    # Try to compile the Python file to check for syntax errors
    $content = Get-Content -Path $file.FullName -Raw
    try {
        $null = [System.Text.Encoding]::UTF8.GetString([System.Text.Encoding]::Default.GetBytes($content))
        python -m py_compile $file.FullName 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Syntax OK" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Syntax error" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ Encoding issue: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n✅ File verification complete" -ForegroundColor Green