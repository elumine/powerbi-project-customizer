@echo off
setlocal
cd /d "%~dp0.."
python -m PyInstaller --onefile --windowed --name Project1 --add-data "src\app\ui\qml;app\ui\qml" --add-data "src\app\ui\styles;app\ui\styles" --add-data "content;content" "src\main.py"