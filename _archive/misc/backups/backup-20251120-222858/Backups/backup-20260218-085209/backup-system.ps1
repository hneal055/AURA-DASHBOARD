Write-Host "💾 SETTING UP BACKUP SYSTEM" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Create backup directory structure
$backupDir = "Backups"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$currentBackup = "$backupDir/backup-$timestamp"

if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

Write-Host "`n1. Backing up Docker configuration..." -ForegroundColor White

# Backup critical files
$filesToBackup = @(
    "Dockerfile",
    "Dockerfile.secure", 
    "Dockerfile.ssl",
    "nginx-secure.conf",
    "nginx-ssl.conf",
    "index.html",
    "*.ps1"
)

New-Item -ItemType Directory -Path "$currentBackup" | Out-Null

foreach ($pattern in $filesToBackup) {
    Get-ChildItem $pattern -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item $_.FullName "$currentBackup/" -Force
        Write-Host "   ✅ Backed up: $($_.Name)" -ForegroundColor Green
    }
}

Write-Host "`n2. Exporting container configuration..." -ForegroundColor White

# Export container settings
docker inspect aura-dashboard > "$currentBackup/container-inspect.json"
docker image history aura-dashboard > "$currentBackup/image-history.txt"

Write-Host "✅ Container configuration exported" -ForegroundColor Green

Write-Host "`n3. Creating backup script..." -ForegroundColor White

# Create automated backup script
@"
`$backupDir = "Backups"
`$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
`$backupPath = "`$backupDir/backup-`$timestamp"

if (-not (Test-Path `$backupDir)) {
    New-Item -ItemType Directory -Path `$backupDir | Out-Null
}

New-Item -ItemType Directory -Path `$backupPath | Out-Null

# Backup files
Copy-Item "Dockerfile*" `$backupPath -Force
Copy-Item "nginx*.conf" `$backupPath -Force  
Copy-Item "*.ps1" `$backupPath -Force
Copy-Item "index.html" `$backupPath -Force

# Export container info
docker inspect aura-dashboard > "`$backupPath/container-inspect.json"
docker image history aura-dashboard > "`$backupPath/image-history.txt"

Write-Host "✅ Backup created: `$backupPath" -ForegroundColor Green

# Clean old backups (keep last 10)
Get-ChildItem `$backupDir -Directory | Sort-Object CreationTime -Descending | Select-Object -Skip 10 | Remove-Item -Recurse -Force
"@ | Set-Content "auto-backup.ps1"

Write-Host "✅ Automated backup script created" -ForegroundColor Green

Write-Host "`n4. Creating restore script..." -ForegroundColor White

# Create restore script
@"
Write-Host "🔄 RESTORE SYSTEM FROM BACKUP" -ForegroundColor Cyan

if (`$args.Count -eq 0) {
    Write-Host "Usage: .\restore-backup.ps1 <backup-folder>" -ForegroundColor Yellow
    Write-Host "Available backups:" -ForegroundColor White
    Get-ChildItem "Backups" -Directory | ForEach-Object { Write-Host "  • `$(`_.Name)" }
    exit 1
}

`$backupFolder = `$args[0]
`$backupPath = "Backups/`$backupFolder"

if (-not (Test-Path `$backupPath)) {
    Write-Host "❌ Backup folder not found: `$backupFolder" -ForegroundColor Red
    exit 1
}

Write-Host "Restoring from backup: `$backupFolder" -ForegroundColor White

# Stop and remove current container
docker stop aura-dashboard 2>`$null
docker rm aura-dashboard 2>`$null

# Restore files
Copy-Item "`$backupPath/*" . -Recurse -Force

Write-Host "✅ Files restored successfully" -ForegroundColor Green
Write-Host "💡 Rebuild and restart container:" -ForegroundColor White
Write-Host "   docker build -t aura-dashboard ." -ForegroundColor Gray
Write-Host "   docker run -d -p 8080:80 --name aura-dashboard aura-dashboard" -ForegroundColor Gray
"@ | Set-Content "restore-backup.ps1"

Write-Host "✅ Restore script created" -ForegroundColor Green

Write-Host "`n🎉 BACKUP SYSTEM READY!" -ForegroundColor Green
Write-Host "📊 Backup location: $currentBackup" -ForegroundColor Cyan
Write-Host "🔧 Available commands:" -ForegroundColor White
Write-Host "   • .\auto-backup.ps1     - Create new backup" -ForegroundColor Gray
Write-Host "   • .\restore-backup.ps1  - Restore from backup" -ForegroundColor Gray