param(
    [Parameter(Mandatory=$true)]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$Username,
    
    [Parameter(Mandatory=$false)]
    [string]$Password,
    
    [Parameter(Mandatory=$false)]
    [string]$Role = "user"
)

$authDir = "auth"
$htpasswdFile = "$authDir/.htpasswd"

function Add-User {
    param([string]$User, [string]$Pass, [string]$UserRole)
    
    if (-not (Test-Path $htpasswdFile)) {
        Write-Host "❌ Authentication file not found" -ForegroundColor Red
        exit 1
    }
    
    # In production, use: htpasswd -b $htpasswdFile $User $Pass
    # For demo, we'll append to file (plain text - NOT for production!)
    "$User:$Pass # Role: $UserRole" | Add-Content "$authDir/users.txt"
    
    Write-Host "✅ User $User added with role $UserRole" -ForegroundColor Green
    Write-Host "⚠️  Note: In production, use proper password hashing!" -ForegroundColor Yellow
}

function Remove-User {
    param([string]$User)
    
    if (Test-Path "$authDir/users.txt") {
        $content = Get-Content "$authDir/users.txt" | Where-Object { $_ -notlike "$User:*" }
        $content | Set-Content "$authDir/users.txt"
        Write-Host "✅ User $User removed" -ForegroundColor Green
    }
}

function List-Users {
    if (Test-Path "$authDir/users.txt") {
        Write-Host "
📋 Registered Users:" -ForegroundColor White
        Get-Content "$authDir/users.txt" | ForEach-Object {
            Write-Host "   • $_" -ForegroundColor Gray
        }
    } else {
        Write-Host "No additional users registered" -ForegroundColor Yellow
    }
}

# Main execution
switch ($Action.ToLower()) {
    "add" {
        if (-not $Username -or -not $Password) {
            Write-Host "❌ Username and Password required for add action" -ForegroundColor Red
            exit 1
        }
        Add-User -User $Username -Pass $Password -UserRole $Role
    }
    "remove" {
        if (-not $Username) {
            Write-Host "❌ Username required for remove action" -ForegroundColor Red
            exit 1
        }
        Remove-User -User $Username
    }
    "list" {
        List-Users
    }
    default {
        Write-Host "❌ Invalid action. Use: add, remove, list" -ForegroundColor Red
        Write-Host "
Usage examples:" -ForegroundColor White
        Write-Host "  .\manage-users.ps1 add -Username john -Password pass123 -Role admin" -ForegroundColor Gray
        Write-Host "  .\manage-users.ps1 remove -Username john" -ForegroundColor Gray
        Write-Host "  .\manage-users.ps1 list" -ForegroundColor Gray
    }
}
