@echo off
setlocal
set PYTHONUTF8=1
cd /d "%~dp0"

echo ===============================
echo Checking Python dependencies...
echo ===============================

python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.10+
    pause
    exit /b
)

echo Installing from requirements.txt...
python -m pip install -r requirements.txt

echo ===============================
echo Running main.py...
echo ===============================
python main.py

pause
endlocal
