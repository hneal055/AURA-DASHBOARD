# Verify Backend Files Exist
Write-Host "🔍 Verifying Backend Files" -ForegroundColor Green

# Check critical files exist
$criticalFiles = @(
    "backend/run.py",
    "backend/requirements.txt", 
    "backend/config.py",
    "backend/app/__init__.py",
    "backend/app/models.py",
    "backend/app/auth.py",
    "backend/app/routes.py"
)

Write-Host "`n📋 Checking critical files..." -ForegroundColor Yellow
foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file - MISSING" -ForegroundColor Red
    }
}

# Show backend structure
Write-Host "`n📁 Backend directory structure:" -ForegroundColor Cyan
Get-ChildItem -Path "backend" -Recurse | ForEach-Object {
    $indent = "  " * ($_.FullName.Split('\').Length - $PWD.Path.Split('\').Length - 1)
    Write-Host "$indent📄 $($_.Name)" -ForegroundColor Gray
}