@echo off
cd /d %~dp0
pip install -r requirements.txt
python script_parser.py
pause
