REM Get-Process git -ErrorAction SilentlyContinue
REM Remove-Item -LiteralPath "../../../../.git/index.lock"

@echo off
del /F /Q "..\..\..\..\.git\index.lock" 2>nul
git status