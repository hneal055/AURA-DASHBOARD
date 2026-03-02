### **COMPLETE STARTUP PROCESS**



\# 1. Activate virtual environment

\& C:/Users/hneal/OneDrive/Desktop/production-parser/venv/Scripts/Activate.ps1



\# 2. Set API key (MUST DO THIS EVERY TIME!)

$env:ANTHROPIC\_API\_KEY = "sk-ant-api03-YOUR-NEW-KEY-HERE"



\# 3. Verify it's set

python -c "import os; print('Key set:', 'YES' if os.environ.get('ANTHROPIC\_API\_KEY') else 'NO')"



\# 4. Start server

python app.py

