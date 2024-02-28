@echo off
cd /D %~dp0
cd .venv/Scripts
call activate.bat
cd ../../
call pip install -r "requirements.txt"