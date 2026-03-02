# Verification Script - Save as verify_setup.ps1
Write-Host "🔍 Verifying Production Parser Project Structure..." -ForegroundColor Blue

# Expected directories
$expectedDirectories = @(
    ".vscode",
    "src",
    "src/parsers",
    "src/analysis",
    "src/visualization",
    "src/utils",
    "tests",
    "data",
    "data/input",
    "data/output",
    "docs",
    "notebooks",
    "scripts"
)

# Expected files
$expectedFiles = @(
    ".vscode/settings.json",
    ".vscode/launch.json",
    "src/__init__.py",
    "src/parsers/__init__.py",
    "src/analysis/__init__.py",
    "src/visualization/__init__.py",
    "src/utils/__init__.py",
    "src/parsers/budget_parser.py",
    "src/analysis/risk_analyzer.py",
    "src/main.py",
    "tests/test_parser.py",
    "requirements.txt",
    ".gitignore",
    "README.md",
    "setup.py",
    "scripts/run_analysis.ps1"
)

# Check directories
$directoriesOk = $true
Write-Host "`n📁 Checking Directories:" -ForegroundColor Cyan
foreach ($dir in $expectedDirectories) {
    if (Test-Path $dir) {
        Write-Host "  ✅ $dir" -ForegroundColor Green
    }
    else {
        Write-Host "  ❌ $dir - MISSING" -ForegroundColor Red
        $directoriesOk = $false
    }
}

# Check files
$filesOk = $true
Write-Host "`n📄 Checking Files:" -ForegroundColor Cyan
foreach ($file in $expectedFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    }
    else {
        Write-Host "  ❌ $file - MISSING" -ForegroundColor Red
        $filesOk = $false
    }
}

# Check virtual environment
$venvOk = $true
Write-Host "`n🐍 Checking Python Virtual Environment:" -ForegroundColor Cyan
if (Test-Path "venv") {
    if (Test-Path "venv/Scripts/activate" -or Test-Path "venv/bin/activate") {
        Write-Host "  ✅ Virtual Environment" -ForegroundColor Green
    }
    else {
        Write-Host "  ⚠️ Virtual Environment exists but may not be properly configured" -ForegroundColor Yellow
        $venvOk = $false
    }
}
else {
    Write-Host "  ❌ Virtual Environment - MISSING" -ForegroundColor Red
    $venvOk = $false
}

# Overall status
Write-Host "`n📊 Overall Setup Status:" -ForegroundColor Magenta
if ($directoriesOk -and $filesOk -and $venvOk) {
    Write-Host "  ✅ PROJECT STRUCTURE VERIFIED SUCCESSFULLY!" -ForegroundColor Green
}
else {
    Write-Host "  ⚠️ SOME ELEMENTS ARE MISSING OR INCORRECT" -ForegroundColor Yellow
    
    # Provide fix suggestions
    if (-not $directoriesOk -or -not $filesOk) {
        Write-Host "`n🔧 Suggested fixes:" -ForegroundColor Yellow
        Write-Host "  1. Re-run the setup script: .\setup_project.ps1" -ForegroundColor White
        Write-Host "  2. Check for any error messages during setup" -ForegroundColor White
        Write-Host "  3. Manually create any missing directories or files" -ForegroundColor White
    }
    
    if (-not $venvOk) {
        Write-Host "`n🔧 To fix virtual environment issues:" -ForegroundColor Yellow
        Write-Host "  1. Delete the venv directory if it exists: Remove-Item -Recurse -Force venv" -ForegroundColor White
        Write-Host "  2. Create a new virtual environment: python -m venv venv" -ForegroundColor White
        Write-Host "  3. Activate it: .\venv\Scripts\activate" -ForegroundColor White
        Write-Host "  4. Install dependencies: pip install -r requirements.txt" -ForegroundColor White
    }
}

# Content verification for key files (optional)
Write-Host "`n📝 Checking Content of Key Files:" -ForegroundColor Cyan
$keyFilesContent = @(
    @{
        Path        = "src/parsers/budget_parser.py"
        Pattern     = "parse_budget_file"
        Description = "Budget parser function"
    },
    @{
        Path        = "src/analysis/risk_analyzer.py"
        Pattern     = "class RiskAnalyzer"
        Description = "Risk analyzer class"
    },
    @{
        Path        = "src/main.py"
        Pattern     = "def main"
        Description = "Main entry point"
    },
    @{
        Path        = "requirements.txt"
        Pattern     = "pandas"
        Description = "Dependencies list"
    }
)

foreach ($item in $keyFilesContent) {
    if (Test-Path $item.Path) {
        $content = Get-Content $item.Path -Raw
        if ($content -match $item.Pattern) {
            Write-Host "  ✅ $($item.Path) - Contains $($item.Description)" -ForegroundColor Green
        }
        else {
            Write-Host "  ⚠️ $($item.Path) - Does not contain expected $($item.Description)" -ForegroundColor Yellow
        }
    }
}

# Check Python installation
Write-Host "`n🐍 Checking Python Installation:" -ForegroundColor Cyan
try {
    $pythonVersion = python --version
    Write-Host "  ✅ $pythonVersion detected" -ForegroundColor Green
}
catch {
    Write-Host "  ❌ Python may not be installed or not in PATH" -ForegroundColor Red
}

# Display directory tree for visual verification
Write-Host "`n🌳 Directory Tree (First 2 Levels):" -ForegroundColor Cyan
function Show-DirectoryTree {
    param (
        [string]$Path = ".",
        [int]$Depth = 0,
        [int]$MaxDepth = 2,
        [string]$Indent = ""
    )

    if ($Depth -gt $MaxDepth) {
        return
    }

    $items = Get-ChildItem -Path $Path
    foreach ($item in $items) {
        if ($item.Name -eq "venv" -or $item.Name -eq ".git") {
            Write-Host "$Indent├── $($item.Name)/ (contents omitted)" -ForegroundColor DarkGray
            continue
        }
        
        if ($item.PSIsContainer) {
            Write-Host "$Indent├── $($item.Name)/" -ForegroundColor Cyan
            Show-DirectoryTree -Path $item.FullName -Depth ($Depth + 1) -MaxDepth $MaxDepth -Indent "$Indent│   "
        }
        else {
            Write-Host "$Indent├── $($item.Name)" -ForegroundColor White
        }
    }
}

Show-DirectoryTree -Path "."

# Final instructions
Write-Host "`n📘 Next Steps:" -ForegroundColor Blue
Write-Host "  1. Activate the virtual environment: .\venv\Scripts\activate" -ForegroundColor White
Write-Host "  2. Install dependencies: pip install -r requirements.txt" -ForegroundColor White
Write-Host "  3. Open the project in VS Code: code ." -ForegroundColor White
Write-Host "  4. Begin development with the parser implementation in src/parsers/budget_parser.py" -ForegroundColor White