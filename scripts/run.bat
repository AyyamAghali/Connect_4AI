@echo off
REM Connect 4 AI - Startup Script for Windows

REM Change to project root directory
cd /d "%~dp0\.."

echo ==========================================
echo   Connect 4 AI Game - Starting Server
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Display Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%

REM Check if virtual environment exists, if not create one
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo [OK] Dependencies already installed
)

echo.
echo Starting Flask server...
echo Server will be available at: http://localhost:5001
echo Open http://localhost:5001 in your browser to play!
echo.
echo Press Ctrl+C to stop the server
echo ==========================================
echo.

REM Start the Flask server
python app.py

pause
