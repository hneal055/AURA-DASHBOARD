# ============================================================================
# PATH A File Verification Script for Windows
# Save this as: verify-path-a.ps1
# Run with: .\verify-path-a.ps1
# ============================================================================

Write-Host "`n═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   PATH A FILE VERIFICATION" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Define required files
$requiredFiles = @{
    "Existing Files" = @(
        "web_app_enhanced.py",
        "budget_analyzer.py",
        "risk_manager.py",
        "pdf_report_generator.py"
    )
    "NEW PATH A Files" = @(
        "charts_data.py",
        "excel_exporter.py"
    )
    "Static CSS" = @(
        "static\css\modern-styles.css"
    )
    "Static JS" = @(
        "static\js\charts.js"
    )
}

$totalFiles = 0
$foundFiles = 0
$missingFiles = @()

# Check each category
foreach ($category in $requiredFiles.Keys) {
    Write-Host "Checking $category..." -ForegroundColor Yellow
    
    foreach ($file in $requiredFiles[$category]) {
        $totalFiles++
        
        if (Test-Path $file) {
            $size = (Get-Item $file).Length
            $sizeKB = [math]::Round($size / 1KB, 1)
            Write-Host "  ✓ $file ($sizeKB KB)" -ForegroundColor Green
            $foundFiles++
        } else {
            Write-Host "  ✗ MISSING: $file" -ForegroundColor Red
            $missingFiles += $file
        }
    }
    Write-Host ""
}

# Check folders
Write-Host "Checking Folders..." -ForegroundColor Yellow
$folders = @("static", "static\css", "static\js", "uploads", "outputs")
foreach ($folder in $folders) {
    if (Test-Path $folder -PathType Container) {
        Write-Host "  ✓ $folder\" -ForegroundColor Green
    } else {
        Write-Host "  ✗ MISSING: $folder\" -ForegroundColor Red
        Write-Host "    Creating folder..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Force -Path $folder | Out-Null
        Write-Host "    ✓ Created $folder\" -ForegroundColor Green
    }
}
Write-Host ""

# Check Python packages
Write-Host "Checking Python Packages..." -ForegroundColor Yellow
$packages = @("flask", "pandas", "reportlab", "openpyxl")
foreach ($package in $packages) {
    $installed = pip list 2>$null | Select-String $package
    if ($installed) {
        Write-Host "  ✓ $package installed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $package NOT installed" -ForegroundColor Red
        Write-Host "    Install with: pip install $package" -ForegroundColor Yellow
    }
}
Write-Host ""

# Summary
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   SUMMARY" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Found: $foundFiles / $totalFiles files" -ForegroundColor $(if ($foundFiles -eq $totalFiles) { "Green" } else { "Yellow" })

if ($missingFiles.Count -gt 0) {
    Write-Host "`nMISSING FILES:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "  • $file" -ForegroundColor Red
    }
    Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Download missing files from Claude chat" -ForegroundColor White
    Write-Host "2. Place them in the correct locations shown above" -ForegroundColor White
    Write-Host "3. Run this script again to verify" -ForegroundColor White
} else {
    Write-Host "`n✓ ALL FILES PRESENT!" -ForegroundColor Green
    Write-Host "`nYou're ready to integrate PATH A!" -ForegroundColor Green
    Write-Host "Next: Read PATH_A_INTEGRATION_GUIDE.txt" -ForegroundColor Yellow
}

Write-Host "═══════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Pause so user can read
Read-Host "Press Enter to exit"
