###### **start\_services.ps1**



\# start\_services.ps1

Write-Host "🚀 Starting AURA Script Analysis System..." -ForegroundColor Green



\# Check if virtual environment is activated

if (-not $env:VIRTUAL\_ENV) {

    Write-Host "⚠️  Activating virtual environment..." -ForegroundColor Yellow

    .\\venv\_314\\Scripts\\Activate.ps1

}



Write-Host "✅ Virtual environment activated" -ForegroundColor Green



\# Start API Server

Write-Host "`n🌐 Starting API Server (Port 8000)..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PWD'; .\\\\venv\\\_314\\\\Scripts\\\\Activate.ps1; uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload`"" -WindowStyle Normal



\# Wait for API to initialize

Start-Sleep -Seconds 5



\# Start Dashboard

Write-Host "`n📊 Starting Dashboard (Port 8501)..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PWD'; .\\\\venv\\\_314\\\\Scripts\\\\Activate.ps1; streamlit run dashboard/aura\\\_dashboard.py`"" -WindowStyle Normal



Write-Host "`n✅ Services Starting..." -ForegroundColor Green

Write-Host "   • API Server: http://localhost:8000/docs" -ForegroundColor White

Write-Host "   • Dashboard: http://localhost:8501" -ForegroundColor White

Write-Host "`n📝 When Streamlit asks for email, just press ENTER" -ForegroundColor Yellow





###### **stop\_services.ps**1



\# stop\_services.ps1

Write-Host "🛑 Stopping AURA Services..." -ForegroundColor Yellow



\# Kill Python processes (uvicorn and streamlit)

Get-Process python -ErrorAction SilentlyContinue | Where-Object { $\_.ProcessName -eq "python" } | Stop-Process -Force



Write-Host "✅ All services stopped" -ForegroundColor Green









###### **check\_services.ps1**



\# check\_services.ps1

Write-Host "🔍 Checking AURA Services Status..." -ForegroundColor Cyan



$apiStatus = Test-NetConnection -ComputerName localhost -Port 8000

$dashboardStatus = Test-NetConnection -ComputerName localhost -Port 8501



Write-Host "`n📊 Service Status:" -ForegroundColor White

Write-Host "   • API Server (Port 8000): $(if ($apiStatus.TcpTestSucceeded) {'✅ RUNNING'} else {'❌ STOPPED'})" -ForegroundColor $(if ($apiStatus.TcpTestSucceeded) {'Green'} else {'Red'})

Write-Host "   • Dashboard (Port 8501): $(if ($dashboardStatus.TcpTestSucceeded) {'✅ RUNNING'} else {'❌ STOPPED'})" -ForegroundColor $(if ($dashboardStatus.TcpTestSucceeded) {'Green'} else {'Red'})



if ($apiStatus.TcpTestSucceeded -and $dashboardStatus.TcpTestSucceeded) {

    Write-Host "`n🎯 Access Points:" -ForegroundColor White

    Write-Host "   • API Documentation: http://localhost:8000/docs" -ForegroundColor Blue

    Write-Host "   • Dashboard: http://localhost:8501" -ForegroundColor Blue

}







###### **test\_fountain\_system.ps1**



\# test\_fountain\_system.ps1

Write-Host "🧪 Testing Fountain File Processing..." -ForegroundColor Cyan



\# Test with a known working Fountain file

$testContent = @"

Title: System Test Script



INT. TEST ROOM - DAY



TEST\_CHARACTER

This is a system test dialogue line.



ANOTHER\_CHARACTER

Another test line for verification.



EXT. TEST LOCATION - NIGHT



TEST\_CHARACTER

Final test dialogue.

"@



$testFile = "system\_test.fountain"

$testContent | Out-File -FilePath $testFile -Encoding utf8



Write-Host "✅ Created test file: $testFile" -ForegroundColor Green



\# Test the parser directly

python -c "

from src.script\_parser.fountain\_parser import FountainParser

from pathlib import Path



parser = FountainParser()

result = parser.parse\_script\_file(Path('$testFile'))



print('=== SYSTEM TEST RESULTS ===')

print('Title: ' + result\['title'])

print('Scenes: ' + str(len(result\['scenes'])))

print('Characters: ' + str(len(result\['characters'])))

print('Dialogue Blocks: ' + str(len(result\['dialogue\_blocks'])))



if len(result\['scenes']) > 0 and len(result\['characters']) > 0:

    print('🎉 FOUNTAIN SYSTEM: ✅ OPERATIONAL')

else:

    print('❌ FOUNTAIN SYSTEM: ISSUES DETECTED')

"



\# Cleanup

Remove-Item $testFile -ErrorAction SilentlyContinue



Write-Host "`n📋 Next Steps:" -ForegroundColor White

Write-Host "   1. Run start\_services.ps1 to launch system" -ForegroundColor Yellow

Write-Host "   2. Upload Fountain files to http://localhost:8501" -ForegroundColor Yellow

Write-Host "   3. Verify analysis results in dashboard" -ForegroundColor Yellow





###### **Create all management scripts**



\# Create all management scripts

@'

\# start\_services.ps1

Write-Host "🚀 Starting AURA Script Analysis System..." -ForegroundColor Green



if (-not $env:VIRTUAL\_ENV) {

    Write-Host "⚠️  Activating virtual environment..." -ForegroundColor Yellow

    .\\venv\_314\\Scripts\\Activate.ps1

}



Write-Host "✅ Virtual environment activated" -ForegroundColor Green



Write-Host "`n🌐 Starting API Server (Port 8000)..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PWD'; .\\\\venv\\\_314\\\\Scripts\\\\Activate.ps1; uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload`"" -WindowStyle Normal



Start-Sleep -Seconds 5



Write-Host "`n📊 Starting Dashboard (Port 8501)..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PWD'; .\\\\venv\\\_314\\\\Scripts\\\\Activate.ps1; streamlit run dashboard/aura\\\_dashboard.py`"" -WindowStyle Normal



Write-Host "`n✅ Services Starting..." -ForegroundColor Green

Write-Host "   • API Server: http://localhost:8000/docs" -ForegroundColor White

Write-Host "   • Dashboard: http://localhost:8501" -ForegroundColor White

Write-Host "`n📝 When Streamlit asks for email, just press ENTER" -ForegroundColor Yellow

'@ | Out-File -FilePath "start\_services.ps1" -Encoding utf8



@'

\# stop\_services.ps1

Write-Host "🛑 Stopping AURA Services..." -ForegroundColor Yellow

Get-Process python -ErrorAction SilentlyContinue | Where-Object { $\_.ProcessName -eq "python" } | Stop-Process -Force

Write-Host "✅ All services stopped" -ForegroundColor Green

'@ | Out-File -FilePath "stop\_services.ps1" -Encoding utf8



Write-Host "✅ Created service management scripts" -ForegroundColor Gre**en**







\# **Test the complete Fountain system**

.\\test\_fountain\_system.ps1

