$backupDir = "Backups"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupPath = "$backupDir/backup-$timestamp"

if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

New-Item -ItemType Directory -Path $backupPath | Out-Null

# Backup files
Copy-Item "Dockerfile*" $backupPath -Force
Copy-Item "nginx*.conf" $backupPath -Force  
Copy-Item "*.ps1" $backupPath -Force
Copy-Item "index.html" $backupPath -Force

# Export container info
docker inspect aura-dashboard > "$backupPath/container-inspect.json"
docker image history aura-dashboard > "$backupPath/image-history.txt"

Write-Host "✅ Backup created: $backupPath" -ForegroundColor Green

# Clean old backups (keep last 10)
Get-ChildItem $backupDir -Directory | Sort-Object CreationTime -Descending | Select-Object -Skip 10 | Remove-Item -Recurse -Force
