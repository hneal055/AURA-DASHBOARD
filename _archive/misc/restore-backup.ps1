Write-Host "🔄 RESTORE SYSTEM FROM BACKUP" -ForegroundColor Cyan

if ($args.Count -eq 0) {
    Write-Host "Usage: .\restore-backup.ps1 <backup-folder>" -ForegroundColor Yellow
    Write-Host "Available backups:" -ForegroundColor White
    Get-ChildItem "Backups" -Directory | ForEach-Object { Write-Host "  • $(_.Name)" }
    exit 1
}

$backupFolder = $args[0]
$backupPath = "Backups/$backupFolder"

if (-not (Test-Path $backupPath)) {
    Write-Host "❌ Backup folder not found: $backupFolder" -ForegroundColor Red
    exit 1
}

Write-Host "Restoring from backup: $backupFolder" -ForegroundColor White

# Stop and remove current container
docker stop aura-dashboard 2>$null
docker rm aura-dashboard 2>$null

# Restore files
Copy-Item "$backupPath/*" . -Recurse -Force

Write-Host "✅ Files restored successfully" -ForegroundColor Green
Write-Host "💡 Rebuild and restart container:" -ForegroundColor White
Write-Host "   docker build -t aura-dashboard ." -ForegroundColor Gray
Write-Host "   docker run -d -p 8080:80 --name aura-dashboard aura-dashboard" -ForegroundColor Gray
