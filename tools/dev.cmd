@echo off
setlocal
cd /d "%~dp0.."
python "%CD%\src\main.py" %*
